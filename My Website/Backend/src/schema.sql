-- ParaBank Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    phone_number VARCHAR(20),
    ssn VARCHAR(11),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    account_number VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    open_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) REFERENCES accounts(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    date DATE NOT NULL,
    type VARCHAR(20) NOT NULL,
    category VARCHAR(50),
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payees table
CREATE TABLE IF NOT EXISTS payees (
    id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    phone_number VARCHAR(20),
    account_number VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Investment funds (reference data)
CREATE TABLE IF NOT EXISTS investment_funds (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    change NUMERIC(10,2) NOT NULL DEFAULT 0,
    change_percent NUMERIC(6,2) NOT NULL DEFAULT 0
);

-- Portfolio holdings
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) REFERENCES investment_funds(symbol),
    shares NUMERIC(15,4) NOT NULL,
    avg_cost NUMERIC(10,2) NOT NULL,
    market_value NUMERIC(15,2) NOT NULL,
    gain_loss NUMERIC(15,2) NOT NULL DEFAULT 0,
    gain_loss_percent NUMERIC(6,2) NOT NULL DEFAULT 0
);

-- Loans table
CREATE TABLE IF NOT EXISTS loans (
    id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    original_amount NUMERIC(15,2) NOT NULL,
    current_balance NUMERIC(15,2) NOT NULL,
    interest_rate NUMERIC(5,2) NOT NULL,
    monthly_payment NUMERIC(10,2) NOT NULL,
    next_payment_date DATE,
    term_months INTEGER NOT NULL,
    remaining_months INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cards table
CREATE TABLE IF NOT EXISTS cards (
    id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    last4 VARCHAR(4) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    linked_account VARCHAR(20) REFERENCES accounts(id),
    expiry_date VARCHAR(5) NOT NULL,
    spending_limit NUMERIC(10,2),
    daily_limit NUMERIC(10,2),
    available_credit NUMERIC(10,2),
    travel_notice_start DATE,
    travel_notice_end DATE,
    travel_notice_destination VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support messages table
CREATE TABLE IF NOT EXISTS support_messages (
    id VARCHAR(30) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    attachment_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Callback requests table
CREATE TABLE IF NOT EXISTS callback_requests (
    id VARCHAR(30) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(255) NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recurring investment plans table
CREATE TABLE IF NOT EXISTS recurring_investment_plans (
    id VARCHAR(30) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) REFERENCES investment_funds(symbol),
    contribution_amount NUMERIC(10,2) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    funding_account VARCHAR(20) REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- E-statement preferences table
CREATE TABLE IF NOT EXISTS e_statement_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    paperless BOOLEAN NOT NULL DEFAULT false,
    email VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
