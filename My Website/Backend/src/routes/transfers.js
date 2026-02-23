import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// POST /api/transfers
router.post("/", async (req, res) => {
  try {
    const { userId, amount, fromAccountId, toAccountId, transferType, externalAccountNumber } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({ error: "Please enter a valid transfer amount" });
    }

    // Prevent same-account internal transfers
    if (transferType === "internal" && fromAccountId === toAccountId) {
      return res.status(400).json({ error: "Source and destination accounts cannot be the same" });
    }

    // Verify source account
    const fromResult = await pool.query(
      "SELECT * FROM accounts WHERE id = $1 AND user_id = $2",
      [fromAccountId, userId]
    );
    if (fromResult.rows.length === 0) {
      return res.status(400).json({ error: "Source account not found" });
    }
    const fromAccount = fromResult.rows[0];
    if (parseFloat(fromAccount.balance) < amount) {
      return res.status(400).json({ error: "Insufficient funds in source account" });
    }

    const client = await pool.connect();
    try {
      await client.query("BEGIN");

      // Debit source
      await client.query(
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        [amount, fromAccountId]
      );

      const txnId = crypto.randomBytes(6).toString("hex").toUpperCase();

      if (transferType === "internal") {
        // Verify destination account
        const toResult = await pool.query(
          "SELECT * FROM accounts WHERE id = $1 AND user_id = $2",
          [toAccountId, userId]
        );
        if (toResult.rows.length === 0) {
          await client.query("ROLLBACK");
          return res.status(400).json({ error: "Destination account not found" });
        }

        // Credit destination
        await client.query(
          "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
          [amount, toAccountId]
        );

        // Record transactions
        const now = new Date().toISOString().split("T")[0];
        await client.query(
          `INSERT INTO transactions (id, account_id, description, amount, date, type, category, transaction_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
          [`txn_${txnId}_from`, fromAccountId, `Transfer to ****${toAccountId.slice(-4)}`, -amount, now, "transfer", "Transfer", `TXN${txnId}_FROM`]
        );
        await client.query(
          `INSERT INTO transactions (id, account_id, description, amount, date, type, category, transaction_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
          [`txn_${txnId}_to`, toAccountId, `Transfer from ****${fromAccountId.slice(-4)}`, amount, now, "credit", "Transfer", `TXN${txnId}_TO`]
        );
      } else {
        // External transfer — just debit and record
        const now = new Date().toISOString().split("T")[0];
        await client.query(
          `INSERT INTO transactions (id, account_id, description, amount, date, type, category, transaction_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
          [`txn_${txnId}`, fromAccountId, `External transfer to ${externalAccountNumber}`, -amount, now, "transfer", "Transfer", `TXN${txnId}`]
        );
      }

      await client.query("COMMIT");

      res.json({
        message: "Transfer completed successfully.",
        transactionId: txnId,
      });
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("Transfer error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
