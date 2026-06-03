import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// GET /api/investments/portfolio?userId=1
router.get("/portfolio", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      `SELECT ph.*, if.name, if.price, if.change, if.change_percent
       FROM portfolio_holdings ph
       JOIN investment_funds if ON ph.symbol = if.symbol
       WHERE ph.user_id = $1
       ORDER BY ph.market_value DESC`,
      [userId]
    );

    const holdings = result.rows.map((row) => ({
      id: row.id,
      symbol: row.symbol,
      name: row.name,
      shares: parseFloat(row.shares),
      avgCost: parseFloat(row.avg_cost),
      currentPrice: parseFloat(row.price),
      marketValue: parseFloat(row.market_value),
      gainLoss: parseFloat(row.gain_loss),
      gainLossPercent: parseFloat(row.gain_loss_percent),
    }));

    const totalMarketValue = holdings.reduce((sum, h) => sum + h.marketValue, 0);
    const totalGainLoss = holdings.reduce((sum, h) => sum + h.gainLoss, 0);

    res.json({ holdings, totalMarketValue, totalGainLoss });
  } catch (err) {
    console.error("Get portfolio error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/investments/funds — list all available funds
router.get("/funds", async (_req, res) => {
  try {
    const result = await pool.query("SELECT * FROM investment_funds ORDER BY symbol");
    const funds = result.rows.map((row) => ({
      symbol: row.symbol,
      name: row.name,
      price: parseFloat(row.price),
      change: parseFloat(row.change),
      changePercent: parseFloat(row.change_percent),
    }));
    res.json(funds);
  } catch (err) {
    console.error("Get funds error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/investments/trade
router.post("/trade", async (req, res) => {
  try {
    const { userId, action, symbol, quantity, accountId } = req.body;

    if (!action || !symbol || !quantity || quantity <= 0 || !accountId) {
      return res.status(400).json({ error: "All fields are required and quantity must be greater than zero" });
    }

    // Verify symbol exists
    const fundResult = await pool.query("SELECT * FROM investment_funds WHERE symbol = $1", [symbol]);
    if (fundResult.rows.length === 0) {
      return res.status(400).json({ error: "Fund symbol not found" });
    }
    const fund = fundResult.rows[0];
    const price = parseFloat(fund.price);
    const totalCost = price * quantity;

    // Verify account
    const acctResult = await pool.query("SELECT * FROM accounts WHERE id = $1 AND user_id = $2", [accountId, userId]);
    if (acctResult.rows.length === 0) {
      return res.status(400).json({ error: "Account not found" });
    }
    const accountBalance = parseFloat(acctResult.rows[0].balance);

    if (action === "Buy") {
      if (accountBalance < totalCost) {
        return res.status(400).json({ error: "Insufficient buying power in selected account" });
      }
    } else if (action === "Sell") {
      // Verify share balance
      const holdingResult = await pool.query(
        "SELECT * FROM portfolio_holdings WHERE user_id = $1 AND symbol = $2",
        [userId, symbol]
      );
      if (holdingResult.rows.length === 0 || parseFloat(holdingResult.rows[0].shares) < quantity) {
        return res.status(400).json({ error: "Insufficient share balance to sell" });
      }
    }

    const client = await pool.connect();
    try {
      await client.query("BEGIN");

      const orderId = `ORD${crypto.randomBytes(6).toString("hex").toUpperCase()}`;

      if (action === "Buy") {
        // Debit account
        await client.query("UPDATE accounts SET balance = balance - $1 WHERE id = $2", [totalCost, accountId]);

        // Update or insert holdings
        const existing = await client.query(
          "SELECT * FROM portfolio_holdings WHERE user_id = $1 AND symbol = $2",
          [userId, symbol]
        );
        if (existing.rows.length > 0) {
          const oldShares = parseFloat(existing.rows[0].shares);
          const oldAvgCost = parseFloat(existing.rows[0].avg_cost);
          const newShares = oldShares + quantity;
          const newAvgCost = ((oldAvgCost * oldShares) + (price * quantity)) / newShares;
          const newMarketValue = newShares * price;
          const newGainLoss = newMarketValue - (newAvgCost * newShares);
          const newGainLossPercent = (newGainLoss / (newAvgCost * newShares)) * 100;
          await client.query(
            `UPDATE portfolio_holdings SET shares = $1, avg_cost = $2, market_value = $3, gain_loss = $4, gain_loss_percent = $5 WHERE user_id = $6 AND symbol = $7`,
            [newShares, newAvgCost.toFixed(2), newMarketValue.toFixed(2), newGainLoss.toFixed(2), newGainLossPercent.toFixed(2), userId, symbol]
          );
        } else {
          await client.query(
            `INSERT INTO portfolio_holdings (user_id, symbol, shares, avg_cost, market_value, gain_loss, gain_loss_percent) VALUES ($1, $2, $3, $4, $5, 0, 0)`,
            [userId, symbol, quantity, price, totalCost.toFixed(2)]
          );
        }
      } else {
        // Sell: credit account
        await client.query("UPDATE accounts SET balance = balance + $1 WHERE id = $2", [totalCost, accountId]);

        const holding = await client.query(
          "SELECT * FROM portfolio_holdings WHERE user_id = $1 AND symbol = $2",
          [userId, symbol]
        );
        const oldShares = parseFloat(holding.rows[0].shares);
        const newShares = oldShares - quantity;
        if (newShares <= 0) {
          await client.query("DELETE FROM portfolio_holdings WHERE user_id = $1 AND symbol = $2", [userId, symbol]);
        } else {
          const avgCost = parseFloat(holding.rows[0].avg_cost);
          const newMarketValue = newShares * price;
          const newGainLoss = newMarketValue - (avgCost * newShares);
          const newGainLossPercent = (newGainLoss / (avgCost * newShares)) * 100;
          await client.query(
            `UPDATE portfolio_holdings SET shares = $1, market_value = $2, gain_loss = $3, gain_loss_percent = $4 WHERE user_id = $5 AND symbol = $6`,
            [newShares, newMarketValue.toFixed(2), newGainLoss.toFixed(2), newGainLossPercent.toFixed(2), userId, symbol]
          );
        }
      }

      await client.query("COMMIT");
      res.json({ message: "Trade executed successfully.", orderId });
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("Trade error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/investments/plan
router.post("/plan", async (req, res) => {
  try {
    const { userId, symbol, contributionAmount, frequency, startDate, fundingAccountId } = req.body;

    if (!symbol || !contributionAmount || !frequency || !startDate || !fundingAccountId) {
      return res.status(400).json({ error: "All fields are required" });
    }

    // Validate symbol
    const fundResult = await pool.query("SELECT * FROM investment_funds WHERE symbol = $1", [symbol]);
    if (fundResult.rows.length === 0) {
      return res.status(400).json({ error: "Fund symbol not found" });
    }

    // Validate start date is in the future
    const start = new Date(startDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (start <= today) {
      return res.status(400).json({ error: "Start date must be in the future" });
    }

    // Validate contribution minimum ($25)
    if (contributionAmount < 25) {
      return res.status(400).json({ error: "Minimum contribution amount is $25" });
    }

    // Validate funding account balance
    const acctResult = await pool.query("SELECT balance FROM accounts WHERE id = $1 AND user_id = $2", [fundingAccountId, userId]);
    if (acctResult.rows.length === 0) {
      return res.status(400).json({ error: "Funding account not found" });
    }
    if (parseFloat(acctResult.rows[0].balance) < contributionAmount) {
      return res.status(400).json({ error: "Insufficient balance in funding account" });
    }

    const planId = `plan_${crypto.randomBytes(4).toString("hex")}`;
    await pool.query(
      `INSERT INTO recurring_investment_plans (id, user_id, symbol, contribution_amount, frequency, start_date, funding_account) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [planId, userId, symbol, contributionAmount, frequency, startDate, fundingAccountId]
    );

    res.status(201).json({ message: "Plan created successfully.", planId });
  } catch (err) {
    console.error("Plan error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
