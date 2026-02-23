import pg from "pg";
import bcrypt from "bcrypt";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
});

async function seed() {
  const client = await pool.connect();
  try {
    // Run schema
    const schema = fs.readFileSync(path.join(__dirname, "schema.sql"), "utf-8");
    await client.query(schema);
    console.log("Schema created successfully.");

    // Clear existing data (in reverse dependency order)
    await client.query("DELETE FROM e_statement_preferences");
    await client.query("DELETE FROM recurring_investment_plans");
    await client.query("DELETE FROM callback_requests");
    await client.query("DELETE FROM support_messages");
    await client.query("DELETE FROM cards");
    await client.query("DELETE FROM loans");
    await client.query("DELETE FROM portfolio_holdings");
    await client.query("DELETE FROM investment_funds");
    await client.query("DELETE FROM payees");
    await client.query("DELETE FROM transactions");
    await client.query("DELETE FROM accounts");
    await client.query("DELETE FROM users");
    console.log("Cleared existing data.");

    // Seed user (password: Admin123!@#)
    const passwordHash = await bcrypt.hash("Admin123!@#", 10);
    const userResult = await client.query(
      `INSERT INTO users (first_name, last_name, email, username, password_hash, street_address, city, state, zip_code, phone_number, ssn)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id`,
      [
        "John", "Doe", "admin@parabank.com", "admin", passwordHash,
        "123 Main Street", "Springfield", "IL", "62701", "(555) 123-4567", "***-**-1234"
      ]
    );
    const userId = userResult.rows[0].id;
    console.log(`User created with id: ${userId}`);

    // Seed accounts
    const accounts = [
      { id: "12345001", type: "Checking", balance: 5847.52, accountNumber: "****5001", status: "Active", openDate: "2023-01-15" },
      { id: "12345002", type: "Savings", balance: 25678.90, accountNumber: "****5002", status: "Active", openDate: "2023-02-20" },
      { id: "12345003", type: "Credit Card", balance: -1534.67, accountNumber: "****5003", status: "Active", openDate: "2023-03-10" },
      { id: "12345004", type: "Loan", balance: -45000.00, accountNumber: "****5004", status: "Active", openDate: "2023-04-05" },
    ];
    for (const a of accounts) {
      await client.query(
        `INSERT INTO accounts (id, user_id, type, balance, account_number, status, open_date) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [a.id, userId, a.type, a.balance, a.accountNumber, a.status, a.openDate]
      );
    }
    console.log("Accounts seeded.");

    // Seed transactions
    const transactions = [
      { id: "txn001", accountId: "12345001", description: "Direct Deposit - Salary", amount: 4200.00, date: "2024-01-15", type: "credit", category: "Income", transactionId: "TXN20240115001" },
      { id: "txn002", accountId: "12345001", description: "Online Purchase - Amazon", amount: -127.45, date: "2024-01-14", type: "debit", category: "Shopping", transactionId: "TXN20240114001" },
      { id: "txn003", accountId: "12345001", description: "Transfer to Savings", amount: -1000.00, date: "2024-01-13", type: "transfer", category: "Transfer", transactionId: "TXN20240113001" },
      { id: "txn004", accountId: "12345002", description: "Transfer from Checking", amount: 1000.00, date: "2024-01-13", type: "credit", category: "Transfer", transactionId: "TXN20240113002" },
      { id: "txn005", accountId: "12345001", description: "ATM Withdrawal", amount: -80.00, date: "2024-01-12", type: "debit", category: "Cash", transactionId: "TXN20240112001" },
      { id: "txn006", accountId: "12345001", description: "Grocery Store - Walmart", amount: -156.78, date: "2024-01-11", type: "debit", category: "Groceries", transactionId: "TXN20240111001" },
      { id: "txn007", accountId: "12345003", description: "Monthly Payment", amount: 250.00, date: "2024-01-10", type: "credit", category: "Payment", transactionId: "TXN20240110001" },
    ];
    for (const t of transactions) {
      await client.query(
        `INSERT INTO transactions (id, account_id, description, amount, date, type, category, transaction_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
        [t.id, t.accountId, t.description, t.amount, t.date, t.type, t.category, t.transactionId]
      );
    }
    console.log("Transactions seeded.");

    // Seed payees
    const payees = [
      { id: "payee001", name: "Electric Company", streetAddress: "456 Power Street", city: "Springfield", state: "IL", zipCode: "62701", phoneNumber: "(555) 987-6543", accountNumber: "ELC123456789" },
      { id: "payee002", name: "Gas Utility", streetAddress: "789 Gas Avenue", city: "Springfield", state: "IL", zipCode: "62701", phoneNumber: "(555) 876-5432", accountNumber: "GAS987654321" },
      { id: "payee003", name: "Internet Provider", streetAddress: "321 Tech Boulevard", city: "Springfield", state: "IL", zipCode: "62701", phoneNumber: "(555) 765-4321", accountNumber: "INT555444333" },
    ];
    for (const p of payees) {
      await client.query(
        `INSERT INTO payees (id, user_id, name, street_address, city, state, zip_code, phone_number, account_number) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
        [p.id, userId, p.name, p.streetAddress, p.city, p.state, p.zipCode, p.phoneNumber, p.accountNumber]
      );
    }
    console.log("Payees seeded.");

    // Seed investment funds
    const funds = [
      { symbol: "VTSAX", name: "Vanguard Total Stock Market Index", price: 112.45, change: 1.23, changePercent: 1.11 },
      { symbol: "VTIAX", name: "Vanguard Total International Stock Index", price: 78.90, change: -0.45, changePercent: -0.57 },
      { symbol: "VBTLX", name: "Vanguard Total Bond Market Index", price: 10.89, change: 0.02, changePercent: 0.18 },
    ];
    for (const f of funds) {
      await client.query(
        `INSERT INTO investment_funds (symbol, name, price, change, change_percent) VALUES ($1, $2, $3, $4, $5)`,
        [f.symbol, f.name, f.price, f.change, f.changePercent]
      );
    }
    console.log("Investment funds seeded.");

    // Seed portfolio holdings
    const holdings = [
      { symbol: "VTSAX", shares: 150.5, avgCost: 108.20, marketValue: 16916.73, gainLoss: 640.73, gainLossPercent: 3.93 },
      { symbol: "VTIAX", shares: 75.0, avgCost: 82.15, marketValue: 5917.50, gainLoss: -243.75, gainLossPercent: -3.96 },
    ];
    for (const h of holdings) {
      await client.query(
        `INSERT INTO portfolio_holdings (user_id, symbol, shares, avg_cost, market_value, gain_loss, gain_loss_percent) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [userId, h.symbol, h.shares, h.avgCost, h.marketValue, h.gainLoss, h.gainLossPercent]
      );
    }
    console.log("Portfolio holdings seeded.");

    // Seed loans
    const loans = [
      { id: "loan001", type: "Auto Loan", originalAmount: 25000.00, currentBalance: 18750.00, interestRate: 4.5, monthlyPayment: 465.32, nextPaymentDate: "2024-02-01", termMonths: 60, remainingMonths: 42 },
      { id: "loan002", type: "Personal Loan", originalAmount: 15000.00, currentBalance: 12500.00, interestRate: 7.2, monthlyPayment: 298.67, nextPaymentDate: "2024-02-15", termMonths: 48, remainingMonths: 38 },
    ];
    for (const l of loans) {
      await client.query(
        `INSERT INTO loans (id, user_id, type, original_amount, current_balance, interest_rate, monthly_payment, next_payment_date, term_months, remaining_months) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [l.id, userId, l.type, l.originalAmount, l.currentBalance, l.interestRate, l.monthlyPayment, l.nextPaymentDate, l.termMonths, l.remainingMonths]
      );
    }
    console.log("Loans seeded.");

    // Seed cards
    const cards = [
      { id: "card001", type: "Debit", last4: "5001", status: "Active", linkedAccount: "12345001", expiryDate: "12/26", spendingLimit: 2500.00, dailyLimit: 500.00, availableCredit: null },
      { id: "card002", type: "Credit", last4: "5003", status: "Active", linkedAccount: "12345003", expiryDate: "08/27", spendingLimit: 5000.00, dailyLimit: null, availableCredit: 3465.33 },
    ];
    for (const c of cards) {
      await client.query(
        `INSERT INTO cards (id, user_id, type, last4, status, linked_account, expiry_date, spending_limit, daily_limit, available_credit) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [c.id, userId, c.type, c.last4, c.status, c.linkedAccount, c.expiryDate, c.spendingLimit, c.dailyLimit, c.availableCredit]
      );
    }
    console.log("Cards seeded.");

    console.log("\nDatabase seeded successfully!");
  } catch (err) {
    console.error("Seeding error:", err);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

seed();
