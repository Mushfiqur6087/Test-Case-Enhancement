import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import authRoutes from "./routes/auth.js";
import accountRoutes from "./routes/accounts.js";
import transactionRoutes from "./routes/transactions.js";
import transferRoutes from "./routes/transfers.js";
import billpayRoutes from "./routes/billpay.js";
import loanRoutes from "./routes/loans.js";
import userRoutes from "./routes/user.js";
import cardRoutes from "./routes/cards.js";
import investmentRoutes from "./routes/investments.js";
import statementRoutes from "./routes/statements.js";
import securityRoutes from "./routes/security.js";
import supportRoutes from "./routes/support.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health check
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok" });
});

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/accounts", accountRoutes);
app.use("/api/transactions", transactionRoutes);
app.use("/api/transfers", transferRoutes);
app.use("/api/billpay", billpayRoutes);
app.use("/api/loans", loanRoutes);
app.use("/api/user", userRoutes);
app.use("/api/cards", cardRoutes);
app.use("/api/investments", investmentRoutes);
app.use("/api/statements", statementRoutes);
app.use("/api/security", securityRoutes);
app.use("/api/support", supportRoutes);

app.listen(PORT, "0.0.0.0", () => {
  console.log(`ParaBank API running on port ${PORT}`);
});
