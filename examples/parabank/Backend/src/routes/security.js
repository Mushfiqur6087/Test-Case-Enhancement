import { Router } from "express";
import pool from "../db.js";
import bcrypt from "bcrypt";

const router = Router();

// POST /api/security/change-password
router.post("/change-password", async (req, res) => {
  try {
    const { userId, currentPassword, newPassword } = req.body;
    if (!userId)
      return res.status(400).json({ error: "userId is required" });
    if (!currentPassword)
      return res.status(400).json({ error: "Current password is required" });
    if (!newPassword)
      return res.status(400).json({ error: "New password is required" });

    // strong password policy: >= 8 chars, uppercase, lowercase, digit, special
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/;
    if (!strongRegex.test(newPassword)) {
      return res.status(400).json({
        error:
          "Password must be at least 8 characters and include uppercase, lowercase, digit, and special character.",
      });
    }

    // look up user
    const userRes = await pool.query("SELECT * FROM users WHERE id = $1", [
      userId,
    ]);
    if (userRes.rows.length === 0)
      return res.status(404).json({ error: "User not found" });

    const user = userRes.rows[0];

    // verify current password
    const match = await bcrypt.compare(currentPassword, user.password_hash);
    if (!match)
      return res
        .status(401)
        .json({ error: "Current password is incorrect" });

    // hash new password and update
    const salt = await bcrypt.genSalt(10);
    const hash = await bcrypt.hash(newPassword, salt);
    await pool.query("UPDATE users SET password_hash = $1 WHERE id = $2", [
      hash,
      userId,
    ]);

    res.json({ message: "Password changed successfully." });
  } catch (err) {
    console.error("Change password error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
