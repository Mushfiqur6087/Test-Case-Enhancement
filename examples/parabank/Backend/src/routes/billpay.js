import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// GET /api/payees?userId=1
router.get("/", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      "SELECT * FROM payees WHERE user_id = $1 ORDER BY name",
      [userId]
    );

    const payees = result.rows.map((row) => ({
      id: row.id,
      name: row.name,
      streetAddress: row.street_address,
      city: row.city,
      state: row.state,
      zipCode: row.zip_code,
      phoneNumber: row.phone_number,
      accountNumber: row.account_number,
    }));

    res.json(payees);
  } catch (err) {
    console.error("Get payees error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/billpay
router.post("/", async (req, res) => {
  try {
    const { userId, payeeName, payeeAccount, amount, sourceAccountId } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({ error: "Please enter a valid payment amount" });
    }

    // Verify source account balance
    const srcResult = await pool.query(
      "SELECT balance FROM accounts WHERE id = $1 AND user_id = $2",
      [sourceAccountId, userId]
    );
    if (srcResult.rows.length === 0) {
      return res.status(400).json({ error: "Source account not found" });
    }
    if (parseFloat(srcResult.rows[0].balance) < amount) {
      return res.status(400).json({ error: "Insufficient funds in source account" });
    }

    const client = await pool.connect();
    try {
      await client.query("BEGIN");

      const refCode = crypto.randomBytes(6).toString("hex").toUpperCase();
      const now = new Date().toISOString().split("T")[0];

      // Debit source account
      await client.query(
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        [amount, sourceAccountId]
      );

      // Record transaction
      await client.query(
        `INSERT INTO transactions (id, account_id, description, amount, date, type, category, transaction_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
        [`bill_${refCode}`, sourceAccountId, `Bill Pay - ${payeeName}`, -amount, now, "debit", "Bill Payment", `BILL${refCode}`]
      );

      await client.query("COMMIT");

      res.json({
        message: "Payment submitted successfully.",
        referenceCode: refCode,
      });
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("Bill pay error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
