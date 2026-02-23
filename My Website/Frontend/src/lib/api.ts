const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:3001/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data as T;
}

// ─── Auth ────────────────────────────────────────────────────────────
export interface LoginResponse {
  message: string;
  user: { id: number; firstName: string; lastName: string; email: string; username: string };
}
export const apiLogin = (username: string, password: string) =>
  request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

export const apiRegister = (data: Record<string, string>) =>
  request<{ message: string }>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── Accounts ────────────────────────────────────────────────────────
export interface Account {
  id: string;
  type: string;
  balance: number;
  accountNumber: string;
  status: string;
  openDate: string;
}
export const apiGetAccounts = (userId: number) =>
  request<Account[]>(`/accounts?userId=${userId}`);

export interface Totals {
  totalBalance: number;
  totalAssets: number;
  totalLiabilities: number;
}
export const apiGetTotals = (userId: number) =>
  request<Totals>(`/accounts/totals?userId=${userId}`);

export const apiOpenAccount = (data: { userId: number; type: string; initialDeposit: number; fundingAccountId: string }) =>
  request<{ message: string; account: { id: string; accountNumber: string; type: string; balance: number } }>("/accounts", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── Transactions ────────────────────────────────────────────────────
export interface Transaction {
  id: string;
  accountId: string;
  description: string;
  amount: number;
  date: string;
  type: string;
  category: string;
  transactionId: string;
}
export const apiGetRecentTransactions = (userId: number, limit = 4) =>
  request<Transaction[]>(`/transactions/recent?userId=${userId}&limit=${limit}`);

// ─── Transfers ───────────────────────────────────────────────────────
export const apiTransfer = (data: {
  userId: number;
  amount: number;
  fromAccountId: string;
  toAccountId?: string;
  transferType: string;
  externalAccountNumber?: string;
}) =>
  request<{ message: string; transactionId: string }>("/transfers", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── Bill Pay ────────────────────────────────────────────────────────
export interface Payee {
  id: string;
  name: string;
  streetAddress: string;
  city: string;
  state: string;
  zipCode: string;
  phoneNumber: string;
  accountNumber: string;
}
export const apiGetPayees = (userId: number) =>
  request<Payee[]>(`/billpay?userId=${userId}`);

export const apiPayBill = (data: {
  userId: number;
  payeeName: string;
  payeeAccount: string;
  amount: number;
  sourceAccountId: string;
}) =>
  request<{ message: string; referenceCode: string }>("/billpay", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── Loans ───────────────────────────────────────────────────────────
export const apiRequestLoan = (data: {
  userId: number;
  loanType: string;
  loanAmount: number;
  downPayment: number;
  collateralAccountId: string;
}) =>
  request<{ message: string; loan?: { accountNumber: string; monthlyPayment: string; rate: number }; denied?: boolean }>("/loans", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── User / Profile ──────────────────────────────────────────────────
export interface UserProfile {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  phone: string;
  address: string;
}
export const apiGetUser = (userId: number) =>
  request<UserProfile>(`/user/${userId}`);

export const apiUpdateUser = (userId: number, data: { firstName: string; lastName: string; email: string; phone: string; address: string }) =>
  request<{ message: string }>(`/user/${userId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

// ─── Cards ───────────────────────────────────────────────────────────
export interface CardInfo {
  id: string;
  cardType: string;
  cardNumber: string;
  accountId: string;
  status: string;
  spendingLimit: number;
  travelNoticeStart: string | null;
  travelNoticeEnd: string | null;
  travelNoticeDestination: string | null;
}
export const apiGetCards = (userId: number) =>
  request<CardInfo[]>(`/cards?userId=${userId}`);

export const apiRequestCard = (data: { userId: number; cardType: string; accountId: string; shippingAddress: string }) =>
  request<{ message: string; trackingId: string }>("/cards/request", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const apiUpdateCardControls = (cardId: string, data: { userId: number; spendingLimit?: number; travelNoticeStart?: string; travelNoticeEnd?: string; travelNoticeDestination?: string; status?: string }) =>
  request<{ message: string }>(`/cards/${cardId}/controls`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

// ─── Investments ─────────────────────────────────────────────────────
export interface Holding {
  id: string;
  symbol: string;
  name: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  marketValue: number;
  gainLoss: number;
  gainLossPercent: number;
}
export interface Fund {
  symbol: string;
  name: string;
  price: number;
  category: string;
}
export const apiGetPortfolio = (userId: number) =>
  request<{ holdings: Holding[]; totalMarketValue: number; totalGainLoss: number }>(`/investments/portfolio?userId=${userId}`);

export const apiGetFunds = () =>
  request<Fund[]>("/investments/funds");

export const apiExecuteTrade = (data: { userId: number; action: string; symbol: string; quantity: number; accountId: string }) =>
  request<{ message: string; orderId: string }>("/investments/trade", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const apiCreatePlan = (data: { userId: number; symbol: string; contributionAmount: number; frequency: string; startDate: string; fundingAccountId: string }) =>
  request<{ message: string }>("/investments/plan", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── Account Statements ─────────────────────────────────────────────
export const apiGenerateStatement = (userId: number, accountId: string, startDate: string, endDate: string) =>
  request<{ message: string; transactions: Transaction[]; count: number }>(`/statements?userId=${userId}&accountId=${accountId}&startDate=${startDate}&endDate=${endDate}`);

export const apiGetStatementPrefs = (userId: number) =>
  request<{ paperless: boolean; email: string }>(`/statements/preferences?userId=${userId}`);

export const apiSaveStatementPrefs = (userId: number, paperless: boolean, email: string) =>
  request<{ message: string }>("/statements/preferences", {
    method: "POST",
    body: JSON.stringify({ userId, paperless, email }),
  });

// ─── Security ────────────────────────────────────────────────────────
export const apiChangePassword = (userId: number, currentPassword: string, newPassword: string) =>
  request<{ message: string }>("/security/change-password", {
    method: "POST",
    body: JSON.stringify({ userId, currentPassword, newPassword }),
  });

// ─── Support ─────────────────────────────────────────────────────────
export const apiSendSupportMessage = (data: { userId: number; subject: string; category: string; messageBody: string; attachmentName?: string }) =>
  request<{ message: string; ticketId: string }>("/support/message", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const apiRequestCallback = (data: { userId: number; reason: string; preferredDate: string; preferredTimeWindow: string; phone: string }) =>
  request<{ message: string }>("/support/callback", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ─── User session helpers ────────────────────────────────────────────
export function saveUser(user: LoginResponse["user"]) {
  sessionStorage.setItem("user", JSON.stringify(user));
}
export function getUser(): (LoginResponse["user"] & { phone?: string }) | null {
  const raw = sessionStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}
export function clearUser() {
  sessionStorage.removeItem("user");
}
