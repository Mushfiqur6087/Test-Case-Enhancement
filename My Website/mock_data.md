# ParaBank Mock Data

All seed data is loaded by `Backend/src/seed.js` against the schema in `Backend/src/schema.sql`.

---

## Database Connection

| Parameter | Value |
|-----------|-------|
| Engine | PostgreSQL 16 (Alpine) |
| Database | `parabank` |
| User | `parabank` |
| Password | `parabank` |
| Connection URL | `postgres://parabank:parabank@db:5432/parabank` |
| Host port | `5432` |

---

## User

Only one user is seeded.

| Field | Value |
|-------|-------|
| First Name | John |
| Last Name | Doe |
| Email | admin@parabank.com |
| Username | admin |
| Password (plain) | `Admin123!@#` |
| Street Address | 123 Main Street |
| City | Springfield |
| State | IL |
| Zip Code | 62701 |
| Phone | (555) 123-4567 |
| SSN | \*\*\*-\*\*-1234 |

---

## Accounts (4)

| ID | Type | Balance | Account # | Status | Open Date |
|----|------|---------|-----------|--------|-----------|
| 12345001 | Checking | $5,847.52 | \*\*\*\*5001 | Active | 2023-01-15 |
| 12345002 | Savings | $25,678.90 | \*\*\*\*5002 | Active | 2023-02-20 |
| 12345003 | Credit Card | -$1,534.67 | \*\*\*\*5003 | Active | 2023-03-10 |
| 12345004 | Loan | -$45,000.00 | \*\*\*\*5004 | Active | 2023-04-05 |

---

## Transactions (7)

All transactions belong to the seeded user's accounts.

| ID | Account | Description | Amount | Date | Type | Category |
|----|---------|-------------|--------|------|------|----------|
| txn001 | 12345001 (Checking) | Direct Deposit - Salary | +$4,200.00 | 2024-01-15 | credit | Income |
| txn002 | 12345001 (Checking) | Online Purchase - Amazon | -$127.45 | 2024-01-14 | debit | Shopping |
| txn003 | 12345001 (Checking) | Transfer to Savings | -$1,000.00 | 2024-01-13 | transfer | Transfer |
| txn004 | 12345002 (Savings) | Transfer from Checking | +$1,000.00 | 2024-01-13 | credit | Transfer |
| txn005 | 12345001 (Checking) | ATM Withdrawal | -$80.00 | 2024-01-12 | debit | Cash |
| txn006 | 12345001 (Checking) | Grocery Store - Walmart | -$156.78 | 2024-01-11 | debit | Groceries |
| txn007 | 12345003 (Credit Card) | Monthly Payment | +$250.00 | 2024-01-10 | credit | Payment |

---

## Payees (3)

| ID | Name | Address | City | State | Zip | Phone | Account # |
|----|------|---------|------|-------|-----|-------|-----------|
| payee001 | Electric Company | 456 Power Street | Springfield | IL | 62701 | (555) 987-6543 | ELC123456789 |
| payee002 | Gas Utility | 789 Gas Avenue | Springfield | IL | 62701 | (555) 876-5432 | GAS987654321 |
| payee003 | Internet Provider | 321 Tech Boulevard | Springfield | IL | 62701 | (555) 765-4321 | INT555444333 |

---

## Investment Funds (3)

Reference data (not user-specific).

| Symbol | Name | Price | Change | Change % |
|--------|------|-------|--------|----------|
| VTSAX | Vanguard Total Stock Market Index | $112.45 | +$1.23 | +1.11% |
| VTIAX | Vanguard Total International Stock Index | $78.90 | -$0.45 | -0.57% |
| VBTLX | Vanguard Total Bond Market Index | $10.89 | +$0.02 | +0.18% |

---

## Portfolio Holdings (2)

| Symbol | Shares | Avg Cost | Market Value | Gain/Loss | Gain/Loss % |
|--------|--------|----------|--------------|-----------|-------------|
| VTSAX | 150.5 | $108.20 | $16,916.73 | +$640.73 | +3.93% |
| VTIAX | 75.0 | $82.15 | $5,917.50 | -$243.75 | -3.96% |

**Total portfolio value:** $22,834.23

---

## Loans (2)

| ID | Type | Original Amount | Current Balance | Rate | Monthly Payment | Next Payment | Term | Remaining |
|----|------|-----------------|-----------------|------|----------------|--------------|------|-----------|
| loan001 | Auto Loan | $25,000.00 | $18,750.00 | 4.5% | $465.32 | 2024-02-01 | 60 months | 42 months |
| loan002 | Personal Loan | $15,000.00 | $12,500.00 | 7.2% | $298.67 | 2024-02-15 | 48 months | 38 months |

---

## Cards (2)

| ID | Type | Last 4 | Status | Linked Account | Expiry | Spending Limit | Daily Limit | Available Credit |
|----|------|--------|--------|----------------|--------|----------------|-------------|------------------|
| card001 | Debit | 5001 | Active | 12345001 (Checking) | 12/26 | $2,500.00 | $500.00 | — |
| card002 | Credit | 5003 | Active | 12345003 (Credit Card) | 08/27 | $5,000.00 | — | $3,465.33 |

---

## Empty Tables (seeded with schema only)

The following tables exist but have **no seed data**. They are populated at runtime through user actions:

| Table | Purpose |
|-------|---------|
| `support_messages` | Secure messages sent via Support Center |
| `callback_requests` | Callback requests submitted via Support Center |
| `recurring_investment_plans` | Recurring investment plans created in Investments |
| `e_statement_preferences` | Paperless e-statement opt-in preferences |

