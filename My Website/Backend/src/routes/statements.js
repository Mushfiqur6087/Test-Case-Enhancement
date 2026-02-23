import { Router } from "express";
import pool from "../db.js";

const router = Router();

// GET /api/statements?userId=1&accountId=xxx&startDate=2024-01-01&endDate=2024-01-31
router.get("/", async (req, res) => {
  try {
    const { userId, accountId, startDate, endDate } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });
    if (!accountId) return res.status(400).json({ error: "accountId is required" });
    if (!startDate || !endDate)
      return res.status(400).json({ error: "startDate and endDate are required" });

    const start = new Date(startDate);
    const end = new Date(endDate);
    if (isNaN(start.getTime()) || isNaN(end.getTime()))
      return res.status(400).json({ error: "Invalid date format" });
    if (start > end)
      return res.status(400).json({ error: "Start date must be before end date" });

    // verify account belongs to user
    const acctCheck = await pool.query(
      "SELECT id FROM accounts WHERE id = $1 AND user_id = $2",
      [accountId, userId]
    );
    if (acctCheck.rows.length === 0)
      return res.status(404).json({ error: "Account not found" });

    const result = await pool.query(
      `SELECT * FROM transactions
       WHERE account_id = $1 AND date >= $2 AND date <= $3
       ORDER BY date DESC`,
      [accountId, startDate, endDate]
    );

    const transactions = result.rows.map((row) => ({
      id: row.id,
      accountId: row.account_id,
      description: row.description,
      amount: parseFloat(row.amount),
      date: row.date,
      type: row.type,
      category: row.category,
      transactionId: row.transaction_id,
    }));

    res.json({
      message: "Statement generated successfully.",
      period: { startDate, endDate },
      accountId,
      transactions,
      count: transactions.length,
    });
  } catch (err) {
    console.error("Generate statement error:", err);
    res.status(500).json({ error: "Unable to generate statement — please try again later." });
  }
});

// GET /api/statements/preferences?userId=1
router.get("/preferences", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      "SELECT * FROM e_statement_preferences WHERE user_id = $1",
      [userId]
    );

    res.json(
      result.rows.length > 0
        ? {
            paperless: result.rows[0].paperless,
            email: result.rows[0].email,
          }
        : { paperless: false, email: "" }
    );
  } catch (err) {
    console.error("Get preferences error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/statements/preferences
router.post("/preferences", async (req, res) => {
  try {
    const { userId, paperless, email } = req.body;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    if (paperless && !email) {
      return res
        .status(400)
        .json({ error: "Email address is required for paperless statements" });
    }
    if (email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({ error: "Invalid email address" });
      }
    }

    // upsert preference
    const existing = await pool.query(
      "SELECT id FROM e_statement_preferences WHERE user_id = $1",
      [userId]
    );

    if (existing.rows.length > 0) {
      await pool.query(
        "UPDATE e_statement_preferences SET paperless = $1, email = $2, updated_at = NOW() WHERE user_id = $3",
        [!!paperless, email || null, userId]
      );
    } else {
      await pool.query(
        "INSERT INTO e_statement_preferences (user_id, paperless, email) VALUES ($1, $2, $3)",
        [userId, !!paperless, email || null]
      );
    }

    res.json({ message: "e-Statement preference updated." });
  } catch (err) {
    console.error("Save preferences error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
