import { Router } from "express";
import pool from "../db.js";

const router = Router();

// GET /api/accounts?userId=1
router.get("/", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      "SELECT * FROM accounts WHERE user_id = $1 ORDER BY open_date ASC",
      [userId]
    );

    const accounts = result.rows.map((row) => ({
      id: row.id,
      type: row.type,
      balance: parseFloat(row.balance),
      accountNumber: row.account_number,
      status: row.status,
      openDate: row.open_date,
    }));

    res.json(accounts);
  } catch (err) {
    console.error("Get accounts error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/accounts/totals?userId=1
router.get("/totals", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      "SELECT balance, type FROM accounts WHERE user_id = $1",
      [userId]
    );

    const accounts = result.rows;
    const totalBalance = accounts.reduce((sum, a) => sum + parseFloat(a.balance), 0);
    const totalAssets = accounts.filter(a => parseFloat(a.balance) > 0).reduce((sum, a) => sum + parseFloat(a.balance), 0);
    const totalLiabilities = Math.abs(accounts.filter(a => parseFloat(a.balance) < 0).reduce((sum, a) => sum + parseFloat(a.balance), 0));

    res.json({ totalBalance, totalAssets, totalLiabilities });
  } catch (err) {
    console.error("Get totals error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/accounts  — Open new account
router.post("/", async (req, res) => {
  try {
    const { userId, type, initialDeposit, fundingAccountId } = req.body;

    // Validate minimum deposit based on account type
    const minimumDeposits = { Checking: 25, Savings: 100 };
    const minDeposit = minimumDeposits[type];
    if (minDeposit && initialDeposit < minDeposit) {
      return res.status(400).json({ error: `Minimum deposit for ${type} account is $${minDeposit}` });
    }

    // Validate funding account balance
    const fundingResult = await pool.query("SELECT balance FROM accounts WHERE id = $1 AND user_id = $2", [fundingAccountId, userId]);
    if (fundingResult.rows.length === 0) {
      return res.status(400).json({ error: "Funding account not found" });
    }
    const fundingBalance = parseFloat(fundingResult.rows[0].balance);
    if (fundingBalance < initialDeposit) {
      return res.status(400).json({ error: "Insufficient funds in funding account" });
    }

    const client = await pool.connect();
    try {
      await client.query("BEGIN");

      // Generate new account id
      const newId = `${Date.now()}`;
      const last4 = newId.slice(-4);
      const accountNumber = `****${last4}`;

      // Create new account
      await client.query(
        `INSERT INTO accounts (id, user_id, type, balance, account_number, status, open_date) VALUES ($1, $2, $3, $4, $5, 'Active', CURRENT_DATE)`,
        [newId, userId, type, initialDeposit, accountNumber]
      );

      // Debit funding account
      await client.query(
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        [initialDeposit, fundingAccountId]
      );

      await client.query("COMMIT");

      res.status(201).json({
        message: "Account opened successfully!",
        account: { id: newId, accountNumber, type, balance: initialDeposit },
      });
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("Open account error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
