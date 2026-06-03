import { Router } from "express";
import bcrypt from "bcrypt";
import pool from "../db.js";

const router = Router();

// POST /api/auth/login
router.post("/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ error: "Username and password are required" });
    }

    const result = await pool.query(
      "SELECT * FROM users WHERE email = $1 OR username = $1",
      [username]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: "Incorrect email or password. Please try again." });
    }

    const user = result.rows[0];
    const valid = await bcrypt.compare(password, user.password_hash);

    if (!valid) {
      return res.status(401).json({ error: "Incorrect email or password. Please try again." });
    }

    // Return user info (no JWT for simplicity — session-based or token can be added later)
    res.json({
      message: "Signed in successfully.",
      user: {
        id: user.id,
        firstName: user.first_name,
        lastName: user.last_name,
        email: user.email,
        username: user.username,
      },
    });
  } catch (err) {
    console.error("Login error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/auth/register
router.post("/register", async (req, res) => {
  try {
    const {
      firstName, lastName, streetAddress, city, state, zipCode,
      phoneNumber, ssn, username, password,
    } = req.body;

    // Check if user already exists
    const existing = await pool.query(
      "SELECT id FROM users WHERE email = $1 OR username = $1",
      [username]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ error: "A user with this email/username already exists" });
    }

    const passwordHash = await bcrypt.hash(password, 10);

    const result = await pool.query(
      `INSERT INTO users (first_name, last_name, email, username, password_hash, street_address, city, state, zip_code, phone_number, ssn)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id`,
      [firstName, lastName, username, username, passwordHash, streetAddress, city, state, zipCode, phoneNumber, ssn]
    );

    // Create default checking and savings accounts for the new user
    const userId = result.rows[0].id;
    const checkingId = `${Date.now()}01`;
    const savingsId = `${Date.now()}02`;

    await pool.query(
      `INSERT INTO accounts (id, user_id, type, balance, account_number, status, open_date) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_DATE)`,
      [checkingId, userId, "Checking", 0, `****${checkingId.slice(-4)}`, "Active"]
    );
    await pool.query(
      `INSERT INTO accounts (id, user_id, type, balance, account_number, status, open_date) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_DATE)`,
      [savingsId, userId, "Savings", 0, `****${savingsId.slice(-4)}`, "Active"]
    );

    res.status(201).json({ message: "Account created successfully — please sign in." });
  } catch (err) {
    console.error("Register error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
