import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// POST /api/support/message
router.post("/message", async (req, res) => {
  try {
    const { userId, subject, category, messageBody, attachmentName } = req.body;
    if (!userId) return res.status(400).json({ error: "userId is required" });
    if (!subject || subject.trim().length < 3)
      return res.status(400).json({ error: "Subject must be at least 3 characters" });
    if (subject.trim().length > 200)
      return res.status(400).json({ error: "Subject must be 200 characters or fewer" });
    if (!messageBody || messageBody.trim().length === 0)
      return res.status(400).json({ error: "Message body is required" });

    const validCategories = ["Account", "Technical", "Security", "Other"];
    if (!category || !validCategories.includes(category))
      return res.status(400).json({ error: "Category must be one of: " + validCategories.join(", ") });

    // validate attachment type if provided
    if (attachmentName) {
      const allowed = [".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"];
      const ext = attachmentName.substring(attachmentName.lastIndexOf(".")).toLowerCase();
      if (!allowed.includes(ext))
        return res.status(400).json({ error: "Attachment type not allowed. Accepted: " + allowed.join(", ") });
    }

    const ticketId = "TKT-" + crypto.randomBytes(4).toString("hex").toUpperCase();

    await pool.query(
      `INSERT INTO support_messages (user_id, ticket_id, subject, category, message_body, attachment_name)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [userId, ticketId, subject.trim(), category, messageBody.trim(), attachmentName || null]
    );

    res.json({ message: "Message sent successfully.", ticketId });
  } catch (err) {
    console.error("Support message error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/support/callback
router.post("/callback", async (req, res) => {
  try {
    const { userId, reason, preferredDate, preferredTimeWindow, phone } = req.body;
    if (!userId) return res.status(400).json({ error: "userId is required" });
    if (!reason || reason.trim().length === 0)
      return res.status(400).json({ error: "Reason for call is required" });
    if (!preferredDate)
      return res.status(400).json({ error: "Preferred date is required" });
    if (!preferredTimeWindow)
      return res.status(400).json({ error: "Preferred time window is required" });
    if (!phone)
      return res.status(400).json({ error: "Phone number is required" });

    // phone format
    const phoneRegex = /^\d{3}-\d{3}-\d{4}$/;
    if (!phoneRegex.test(phone))
      return res.status(400).json({ error: "Phone must be in format ###-###-####" });

    // date must be at least next business day
    const pDate = new Date(preferredDate + "T00:00:00");
    if (isNaN(pDate.getTime()))
      return res.status(400).json({ error: "Invalid date format" });

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // find next business day from today
    const nextBiz = new Date(today);
    nextBiz.setDate(nextBiz.getDate() + 1);
    while (nextBiz.getDay() === 0 || nextBiz.getDay() === 6) {
      nextBiz.setDate(nextBiz.getDate() + 1);
    }

    if (pDate < nextBiz) {
      return res.status(400).json({ error: "Preferred date must be at least the next business day" });
    }

    const validWindows = ["Morning (9 AM – 12 PM)", "Afternoon (12 PM – 3 PM)", "Evening (3 PM – 6 PM)"];
    if (!validWindows.includes(preferredTimeWindow))
      return res.status(400).json({ error: "Invalid time window" });

    await pool.query(
      `INSERT INTO callback_requests (user_id, reason, preferred_date, preferred_time_window, phone)
       VALUES ($1, $2, $3, $4, $5)`,
      [userId, reason.trim(), preferredDate, preferredTimeWindow, phone]
    );

    res.json({ message: "Callback request submitted." });
  } catch (err) {
    console.error("Callback request error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
