import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// GET /api/cards?userId=1
router.get("/", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: "userId is required" });

    const result = await pool.query(
      "SELECT c.*, a.account_number as linked_account_number, a.type as linked_account_type FROM cards c LEFT JOIN accounts a ON c.linked_account = a.id WHERE c.user_id = $1 ORDER BY c.created_at",
      [userId]
    );

    const cards = result.rows.map((row) => ({
      id: row.id,
      type: row.type,
      last4: row.last4,
      status: row.status,
      linkedAccount: row.linked_account,
      linkedAccountNumber: row.linked_account_number,
      linkedAccountType: row.linked_account_type,
      expiryDate: row.expiry_date,
      spendingLimit: row.spending_limit ? parseFloat(row.spending_limit) : null,
      dailyLimit: row.daily_limit ? parseFloat(row.daily_limit) : null,
      availableCredit: row.available_credit ? parseFloat(row.available_credit) : null,
      travelNoticeStart: row.travel_notice_start,
      travelNoticeEnd: row.travel_notice_end,
      travelNoticeDestination: row.travel_notice_destination,
    }));

    res.json(cards);
  } catch (err) {
    console.error("Get cards error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/cards/request — Request new card
router.post("/request", async (req, res) => {
  try {
    const { userId, cardType, linkedAccountId, shippingAddress } = req.body;

    if (!cardType || !linkedAccountId || !shippingAddress || !shippingAddress.trim()) {
      return res.status(400).json({ error: "All fields are required including a complete shipping address" });
    }

    // Verify account standing
    const acctResult = await pool.query(
      "SELECT * FROM accounts WHERE id = $1 AND user_id = $2",
      [linkedAccountId, userId]
    );
    if (acctResult.rows.length === 0) {
      return res.status(400).json({ error: "Linked account not found" });
    }
    if (acctResult.rows[0].status !== "Active") {
      return res.status(400).json({ error: "Linked account is not in good standing" });
    }

    const trackingId = `TRK${crypto.randomBytes(6).toString("hex").toUpperCase()}`;
    const cardId = `card_${crypto.randomBytes(4).toString("hex")}`;
    const last4 = Math.floor(1000 + Math.random() * 9000).toString();
    const expiryYear = new Date().getFullYear() + 3;
    const expiryMonth = String(new Date().getMonth() + 1).padStart(2, "0");
    const expiryDate = `${expiryMonth}/${String(expiryYear).slice(-2)}`;

    await pool.query(
      `INSERT INTO cards (id, user_id, type, last4, status, linked_account, expiry_date, spending_limit, daily_limit)
       VALUES ($1, $2, $3, $4, 'Active', $5, $6, $7, $8)`,
      [cardId, userId, cardType, last4, linkedAccountId, expiryDate, cardType === "Credit" ? 5000 : 2500, cardType === "Debit" ? 500 : null]
    );

    res.status(201).json({
      message: "Card request submitted successfully.",
      trackingId,
    });
  } catch (err) {
    console.error("Card request error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// PUT /api/cards/:id/controls — Update card controls
router.put("/:id/controls", async (req, res) => {
  try {
    const { id } = req.params;
    const { userId, spendingLimit, travelNoticeStart, travelNoticeEnd, travelNoticeDestination, status } = req.body;

    // Verify card belongs to user
    const cardResult = await pool.query(
      "SELECT * FROM cards WHERE id = $1 AND user_id = $2",
      [id, userId]
    );
    if (cardResult.rows.length === 0) {
      return res.status(404).json({ error: "Card not found" });
    }

    const card = cardResult.rows[0];

    // Validate spending limit
    if (spendingLimit !== undefined && spendingLimit !== null) {
      if (isNaN(spendingLimit) || spendingLimit < 0) {
        return res.status(400).json({ error: "Spending limit must be a valid positive number" });
      }
      if (spendingLimit > 50000) {
        return res.status(400).json({ error: "Spending limit cannot exceed $50,000 (policy maximum)" });
      }
    }

    // Validate travel notice dates
    if (travelNoticeStart && travelNoticeEnd) {
      const start = new Date(travelNoticeStart);
      const end = new Date(travelNoticeEnd);
      if (end <= start) {
        return res.status(400).json({ error: "Travel notice end date must be after start date" });
      }
    }

    // Validate status transition
    if (status && !["Active", "Frozen"].includes(status)) {
      return res.status(400).json({ error: "Card status must be Active or Frozen" });
    }

    await pool.query(
      `UPDATE cards SET
        spending_limit = COALESCE($1, spending_limit),
        travel_notice_start = $2,
        travel_notice_end = $3,
        travel_notice_destination = $4,
        status = COALESCE($5, status)
       WHERE id = $6`,
      [spendingLimit, travelNoticeStart || null, travelNoticeEnd || null, travelNoticeDestination || null, status, id]
    );

    res.json({ message: "Card controls updated successfully." });
  } catch (err) {
    console.error("Card controls error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
