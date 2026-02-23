// Mock data for ParaBank application

// Mock user credentials
export const MOCK_CREDENTIALS = {
  email: "admin@parabank.com",
  username: "admin",
  password: "Admin123!@#",
};

// Mock user profile
export const MOCK_USER_PROFILE = {
  firstName: "John",
  lastName: "Doe",
  email: "admin@parabank.com",
  streetAddress: "123 Main Street",
  city: "Springfield",
  state: "IL",
  zipCode: "62701",
  phoneNumber: "(555) 123-4567",
  ssn: "***-**-1234",
};

// Mock accounts data
export const MOCK_ACCOUNTS = [
  {
    id: "12345001",
    type: "Checking",
    balance: 5847.52,
    accountNumber: "****5001",
    status: "Active",
    openDate: "2023-01-15",
  },
  {
    id: "12345002",
    type: "Savings",
    balance: 25678.90,
    accountNumber: "****5002",
    status: "Active",
    openDate: "2023-02-20",
  },
  {
    id: "12345003",
    type: "Credit Card",
    balance: -1534.67,
    accountNumber: "****5003",
    status: "Active",
    openDate: "2023-03-10",
  },
  {
    id: "12345004",
    type: "Loan",
    balance: -45000.00,
    accountNumber: "****5004",
    status: "Active",
    openDate: "2023-04-05",
  },
];

// Mock transactions
export const MOCK_TRANSACTIONS = [
  {
    id: "txn001",
    accountId: "12345001",
    description: "Direct Deposit - Salary",
    amount: 4200.00,
    date: "2024-01-15",
    type: "credit",
    category: "Income",
    transactionId: "TXN20240115001",
  },
  {
    id: "txn002",
    accountId: "12345001",
    description: "Online Purchase - Amazon",
    amount: -127.45,
    date: "2024-01-14",
    type: "debit",
    category: "Shopping",
    transactionId: "TXN20240114001",
  },
  {
    id: "txn003",
    accountId: "12345001",
    description: "Transfer to Savings",
    amount: -1000.00,
    date: "2024-01-13",
    type: "transfer",
    category: "Transfer",
    transactionId: "TXN20240113001",
  },
  {
    id: "txn004",
    accountId: "12345002",
    description: "Transfer from Checking",
    amount: 1000.00,
    date: "2024-01-13",
    type: "credit",
    category: "Transfer",
    transactionId: "TXN20240113002",
  },
  {
    id: "txn005",
    accountId: "12345001",
    description: "ATM Withdrawal",
    amount: -80.00,
    date: "2024-01-12",
    type: "debit",
    category: "Cash",
    transactionId: "TXN20240112001",
  },
  {
    id: "txn006",
    accountId: "12345001",
    description: "Grocery Store - Walmart",
    amount: -156.78,
    date: "2024-01-11",
    type: "debit",
    category: "Groceries",
    transactionId: "TXN20240111001",
  },
  {
    id: "txn007",
    accountId: "12345003",
    description: "Monthly Payment",
    amount: 250.00,
    date: "2024-01-10",
    type: "credit",
    category: "Payment",
    transactionId: "TXN20240110001",
  },
];

// Mock payees for bill pay
export const MOCK_PAYEES = [
  {
    id: "payee001",
    name: "Electric Company",
    streetAddress: "456 Power Street",
    city: "Springfield",
    state: "IL",
    zipCode: "62701",
    phoneNumber: "(555) 987-6543",
    accountNumber: "ELC123456789",
  },
  {
    id: "payee002",
    name: "Gas Utility",
    streetAddress: "789 Gas Avenue",
    city: "Springfield",
    state: "IL",
    zipCode: "62701",
    phoneNumber: "(555) 876-5432",
    accountNumber: "GAS987654321",
  },
  {
    id: "payee003",
    name: "Internet Provider",
    streetAddress: "321 Tech Boulevard",
    city: "Springfield",
    state: "IL",
    zipCode: "62701",
    phoneNumber: "(555) 765-4321",
    accountNumber: "INT555444333",
  },
];

// Mock investment funds
export const MOCK_INVESTMENT_FUNDS = [
  {
    symbol: "VTSAX",
    name: "Vanguard Total Stock Market Index",
    price: 112.45,
    change: 1.23,
    changePercent: 1.11,
  },
  {
    symbol: "VTIAX",
    name: "Vanguard Total International Stock Index",
    price: 78.90,
    change: -0.45,
    changePercent: -0.57,
  },
  {
    symbol: "VBTLX",
    name: "Vanguard Total Bond Market Index",
    price: 10.89,
    change: 0.02,
    changePercent: 0.18,
  },
];

// Mock portfolio holdings
export const MOCK_PORTFOLIO = [
  {
    symbol: "VTSAX",
    shares: 150.5,
    avgCost: 108.20,
    marketValue: 16916.73,
    gainLoss: 640.73,
    gainLossPercent: 3.93,
  },
  {
    symbol: "VTIAX",
    shares: 75.0,
    avgCost: 82.15,
    marketValue: 5917.50,
    gainLoss: -243.75,
    gainLossPercent: -3.96,
  },
];

// Mock loan data
export const MOCK_LOANS = [
  {
    id: "loan001",
    type: "Auto Loan",
    originalAmount: 25000.00,
    currentBalance: 18750.00,
    interestRate: 4.5,
    monthlyPayment: 465.32,
    nextPaymentDate: "2024-02-01",
    termMonths: 60,
    remainingMonths: 42,
  },
  {
    id: "loan002",
    type: "Personal Loan",
    originalAmount: 15000.00,
    currentBalance: 12500.00,
    interestRate: 7.2,
    monthlyPayment: 298.67,
    nextPaymentDate: "2024-02-15",
    termMonths: 48,
    remainingMonths: 38,
  },
];

// Mock cards data
export const MOCK_CARDS = [
  {
    id: "card001",
    type: "Debit",
    last4: "5001",
    status: "Active",
    linkedAccount: "12345001",
    expiryDate: "12/26",
    spendingLimit: 2500.00,
    dailyLimit: 500.00,
  },
  {
    id: "card002",
    type: "Credit",
    last4: "5003",
    status: "Active",
    linkedAccount: "12345003",
    expiryDate: "08/27",
    spendingLimit: 5000.00,
    availableCredit: 3465.33,
  },
];

// Authentication function
export const authenticateUser = (usernameOrEmail: string, password: string): boolean => {
  const isValidCredentials = (
    (usernameOrEmail === MOCK_CREDENTIALS.email || usernameOrEmail === MOCK_CREDENTIALS.username) &&
    password === MOCK_CREDENTIALS.password
  );
  return isValidCredentials;
};

// Helper functions for mock data
export const getTotalBalance = (): number => {
  // Include all accounts - this gives the true net worth
  return MOCK_ACCOUNTS.reduce((sum, account) => sum + account.balance, 0);
};

export const getTotalAssets = (): number => {
  // Only positive balances (assets)
  return MOCK_ACCOUNTS
    .filter(account => account.balance > 0)
    .reduce((sum, account) => sum + account.balance, 0);
};

export const getTotalLiabilities = (): number => {
  // Only negative balances (debts) - return as positive number
  return Math.abs(MOCK_ACCOUNTS
    .filter(account => account.balance < 0)
    .reduce((sum, account) => sum + account.balance, 0));
};

export const getDepositAccountsTotal = (): number => {
  // Only checking and savings accounts
  return MOCK_ACCOUNTS
    .filter(account => account.type === "Checking" || account.type === "Savings")
    .reduce((sum, account) => sum + account.balance, 0);
};

export const getAccountById = (id: string) => {
  return MOCK_ACCOUNTS.find(account => account.id === id);
};

export const getTransactionsByAccountId = (accountId: string) => {
  return MOCK_TRANSACTIONS.filter(transaction => transaction.accountId === accountId);
};

export const getRecentTransactions = (limit: number = 5) => {
  return MOCK_TRANSACTIONS
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, limit);
};
