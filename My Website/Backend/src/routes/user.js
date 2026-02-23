import { Router } from "express";
import pool from "../db.js";

const router = Router();

// GET /api/user/:id
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query("SELECT * FROM users WHERE id = $1", [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }
    const user = result.rows[0];
    res.json({
      id: user.id,
      firstName: user.first_name,
      lastName: user.last_name,
      email: user.email,
      username: user.username,
      streetAddress: user.street_address,
      city: user.city,
      state: user.state,
      zipCode: user.zip_code,
      phoneNumber: user.phone_number,
      ssn: user.ssn,
    });
  } catch (err) {
    console.error("Get user error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// PUT /api/user/:id — Update Contact Info
router.put("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { firstName, lastName, streetAddress, city, state, zipCode, phoneNumber } = req.body;

    // Validate required fields
    if (!firstName || !lastName || !streetAddress || !city || !state || !zipCode) {
      return res.status(400).json({ error: "All required fields must be filled" });
    }

    // Validate ZIP code format
    const zipRegex = /^\d{5}(-\d{4})?$/;
    if (!zipRegex.test(zipCode)) {
      return res.status(400).json({ error: "Please enter a valid ZIP code" });
    }

    // Validate phone number format if provided
    if (phoneNumber) {
      const phoneRegex = /^\(\d{3}\) \d{3}-\d{4}$/;
      if (!phoneRegex.test(phoneNumber)) {
        return res.status(400).json({ error: "Phone must be in format (123) 456-7890" });
      }
    }

    const result = await pool.query(
      `UPDATE users SET first_name = $1, last_name = $2, street_address = $3, city = $4, state = $5, zip_code = $6, phone_number = $7, updated_at = CURRENT_TIMESTAMP
       WHERE id = $8 RETURNING *`,
      [firstName, lastName, streetAddress, city, state, zipCode, phoneNumber || null, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    const user = result.rows[0];
    res.json({
      message: "Profile updated successfully.",
      user: {
        id: user.id,
        firstName: user.first_name,
        lastName: user.last_name,
        email: user.email,
        username: user.username,
        streetAddress: user.street_address,
        city: user.city,
        state: user.state,
        zipCode: user.zip_code,
        phoneNumber: user.phone_number,
      },
    });
  } catch (err) {
    console.error("Update user error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
