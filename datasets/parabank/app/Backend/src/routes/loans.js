import { Router } from "express";
import pool from "../db.js";
import crypto from "crypto";

const router = Router();

// POST /api/loans
router.post("/", async (req, res) => {
  try {
    const { userId, loanType, loanAmount, downPayment, collateralAccountId } = req.body;

    // Validate collateral account
    const colResult = await pool.query(
      "SELECT balance FROM accounts WHERE id = $1 AND user_id = $2",
      [collateralAccountId, userId]
    );
    if (colResult.rows.length === 0) {
      return res.status(400).json({ error: "Collateral account not found" });
    }

    const collateralBalance = parseFloat(colResult.rows[0].balance);

    if (downPayment > collateralBalance) {
      return res.status(400).json({ error: "Insufficient funds in collateral account for down payment" });
    }
    if (collateralBalance < loanAmount * 0.2) {
      return res.status(400).json({ error: "Insufficient collateral value (minimum 20% of loan amount required)" });
    }

    // Validate loan amount range based on type
    const ranges = {
      "Personal Loan": { min: 1000, max: 50000 },
      "Auto Loan": { min: 5000, max: 75000 },
      "Home Loan": { min: 50000, max: 500000 },
    };
    const range = ranges[loanType];
    if (!range) {
      return res.status(400).json({ error: "Invalid loan type" });
    }
    if (loanAmount < range.min || loanAmount > range.max) {
      return res.status(400).json({ error: `Loan amount must be between $${range.min.toLocaleString()} and $${range.max.toLocaleString()} for ${loanType}` });
    }

    // Credit underwriting simulation
    const downPaymentRatio = downPayment / loanAmount;
    const isDownPaymentSufficient = downPaymentRatio >= 0.1;
    const randomApproval = Math.random() < 0.8;

    if (!isDownPaymentSufficient || !randomApproval) {
      const reasons = [
        "Insufficient credit history",
        "Debt-to-income ratio too high",
        "Inadequate collateral value",
        "Income verification required",
      ];
      const reason = reasons[Math.floor(Math.random() * reasons.length)];
      return res.status(400).json({
        error: `Loan application denied. Reason: ${reason}. Please contact our loan officer for assistance.`,
        denied: true,
      });
    }

    // Determine interest rate based on loan type
    const rates = { "Personal Loan": 7.5, "Auto Loan": 4.5, "Home Loan": 3.5 };
    const rate = rates[loanType] || 7.5;
    const netLoan = loanAmount - downPayment;
    const termMonths = 60;
    const monthlyRate = rate / 100 / 12;
    const monthlyPayment =
      (netLoan * monthlyRate * Math.pow(1 + monthlyRate, termMonths)) /
      (Math.pow(1 + monthlyRate, termMonths) - 1);

    const client = await pool.connect();
    try {
      await client.query("BEGIN");

      const loanId = `loan_${crypto.randomBytes(4).toString("hex")}`;
      const newAccountId = `${Date.now()}`;
      const last4 = newAccountId.slice(-4);

      // Create loan account
      await client.query(
        `INSERT INTO accounts (id, user_id, type, balance, account_number, status, open_date) VALUES ($1, $2, 'Loan', $3, $4, 'Active', CURRENT_DATE)`,
        [newAccountId, userId, -netLoan, `****${last4}`]
      );

      // Record loan
      await client.query(
        `INSERT INTO loans (id, user_id, type, original_amount, current_balance, interest_rate, monthly_payment, next_payment_date, term_months, remaining_months)
         VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_DATE + INTERVAL '1 month', $8, $8)`,
        [loanId, userId, loanType, loanAmount, netLoan, rate, monthlyPayment.toFixed(2), termMonths]
      );

      await client.query("COMMIT");

      res.status(201).json({
        message: "Loan approved and created successfully!",
        loan: {
          accountNumber: `****${last4}`,
          monthlyPayment: monthlyPayment.toFixed(2),
          rate,
        },
      });
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("Loan error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
