import { Router } from "express";
import pool from "../db.js";

const router = Router();

// GET /api/transactions?accountId=12345001
router.get("/", async (req, res) => {
  try {
    const { accountId } = req.query;
    if (!accountId) return res.status(400).json({ error: "accountId is required" });

    const result = await pool.query(
      "SELECT * FROM transactions WHERE account_id = $1 ORDER BY date DESC",
      [accountId]
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

    res.json(transactions);
  } catch (err) {
    console.error("Get transactions error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/transactions/recent?userId=1&limit=4
router.get("/recent", async (req, res) => {
  try {
    const { userId, limit = 5 } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      `SELECT t.* FROM transactions t
       JOIN accounts a ON t.account_id = a.id
       WHERE a.user_id = $1
       ORDER BY t.date DESC
       LIMIT $2`,
      [userId, parseInt(limit)]
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

    res.json(transactions);
  } catch (err) {
    console.error("Get recent transactions error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
