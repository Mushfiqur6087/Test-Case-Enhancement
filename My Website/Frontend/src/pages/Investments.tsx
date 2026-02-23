import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, TrendingDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { apiGetAccounts, apiGetPortfolio, apiGetFunds, apiExecuteTrade, apiCreatePlan, getUser, type Fund, type Holding } from "@/lib/api";

interface FundingAccount { id: string; name: string; balance: number; }

export default function Investments() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [totalMarketValue, setTotalMarketValue] = useState(0);
  const [totalGainLoss, setTotalGainLoss] = useState(0);
  const [funds, setFunds] = useState<Fund[]>([]);
  const [accounts, setAccounts] = useState<FundingAccount[]>([]);
  const [isTrading, setIsTrading] = useState(false);
  const [isCreatingPlan, setIsCreatingPlan] = useState(false);
  const user = getUser();
  const { toast } = useToast();

  const [tradeForm, setTradeForm] = useState({ action: "", symbol: "", quantity: "", accountId: "" });
  const [tradeErrors, setTradeErrors] = useState<Record<string, string>>({});

  const [planForm, setPlanForm] = useState({ symbol: "", contributionAmount: "", frequency: "", startDate: "", fundingAccountId: "" });
  const [planErrors, setPlanErrors] = useState<Record<string, string>>({});

  const [symbolFilter, setSymbolFilter] = useState("");

  useEffect(() => {
    if (!user) return;
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [portfolio, f, accts] = await Promise.all([
        apiGetPortfolio(user!.id),
        apiGetFunds(),
        apiGetAccounts(user!.id),
      ]);
      setHoldings(portfolio.holdings);
      setTotalMarketValue(portfolio.totalMarketValue);
      setTotalGainLoss(portfolio.totalGainLoss);
      setFunds(f);
      setAccounts(
        accts
          .filter((a) => a.type === "Checking" || a.type === "Savings")
          .map((a) => ({ id: a.id, name: `${a.type} (${a.accountNumber})`, balance: a.balance }))
      );
    } catch (err) {
      console.error("Failed to load investment data", err);
    }
  };

  const filteredFunds = funds.filter(
    (f) => f.symbol.toLowerCase().includes(symbolFilter.toLowerCase()) || f.name.toLowerCase().includes(symbolFilter.toLowerCase())
  );

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);

  // Trade form
  const handleTradeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!tradeForm.action) errs.action = "Select Buy or Sell";
    if (!tradeForm.symbol) errs.symbol = "Select a fund";
    if (!tradeForm.quantity || Number(tradeForm.quantity) <= 0) errs.quantity = "Quantity must be greater than zero";
    if (!tradeForm.accountId) errs.accountId = "Select an account";
    setTradeErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsTrading(true);
    try {
      const res = await apiExecuteTrade({
        userId: user!.id,
        action: tradeForm.action,
        symbol: tradeForm.symbol,
        quantity: Number(tradeForm.quantity),
        accountId: tradeForm.accountId,
      });
      toast({ title: "Trade executed successfully.", description: `Order ID: ${res.orderId}` });
      setTradeForm({ action: "", symbol: "", quantity: "", accountId: "" });
      await loadData();
    } catch (err: any) {
      toast({ title: "Trade failed", description: err.message, variant: "destructive" });
    } finally {
      setIsTrading(false);
    }
  };

  // Plan form
  const handlePlanSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!planForm.symbol) errs.symbol = "Select a fund";
    if (!planForm.contributionAmount || Number(planForm.contributionAmount) < 25) errs.contributionAmount = "Minimum contribution is $25";
    if (!planForm.frequency) errs.frequency = "Select frequency";
    if (!planForm.startDate) errs.startDate = "Start date is required";
    else {
      const start = new Date(planForm.startDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (start <= today) errs.startDate = "Start date must be in the future";
    }
    if (!planForm.fundingAccountId) errs.fundingAccountId = "Select a funding account";
    setPlanErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsCreatingPlan(true);
    try {
      await apiCreatePlan({
        userId: user!.id,
        symbol: planForm.symbol,
        contributionAmount: Number(planForm.contributionAmount),
        frequency: planForm.frequency,
        startDate: planForm.startDate,
        fundingAccountId: planForm.fundingAccountId,
      });
      toast({ title: "Plan created successfully." });
      setPlanForm({ symbol: "", contributionAmount: "", frequency: "", startDate: "", fundingAccountId: "" });
    } catch (err: any) {
      toast({ title: "Plan creation failed", description: err.message, variant: "destructive" });
    } finally {
      setIsCreatingPlan(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <BarChart3 className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Investments</h1>
        <p className="text-muted-foreground">Manage your portfolio, trade funds, and set up recurring plans</p>
      </div>

      {/* Portfolio Snapshot */}
      <Card>
        <CardHeader><CardTitle>Portfolio Snapshot</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Market Value</p>
              <p className="text-2xl font-bold">{formatCurrency(totalMarketValue)}</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground">Unrealised Gain/Loss</p>
              <p className={`text-2xl font-bold ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
                {totalGainLoss >= 0 ? "+" : ""}{formatCurrency(totalGainLoss)}
              </p>
            </div>
          </div>
          {holdings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b">
                  <th className="text-left py-2 px-3">Symbol</th><th className="text-left py-2 px-3">Name</th>
                  <th className="text-right py-2 px-3">Shares</th><th className="text-right py-2 px-3">Price</th>
                  <th className="text-right py-2 px-3">Market Value</th><th className="text-right py-2 px-3">Gain/Loss</th>
                </tr></thead>
                <tbody>
                  {holdings.map((h) => (
                    <tr key={h.id} className="border-b">
                      <td className="py-2 px-3 font-medium">{h.symbol}</td>
                      <td className="py-2 px-3 text-muted-foreground">{h.name}</td>
                      <td className="py-2 px-3 text-right font-mono">{h.shares.toFixed(2)}</td>
                      <td className="py-2 px-3 text-right font-mono">{formatCurrency(h.currentPrice)}</td>
                      <td className="py-2 px-3 text-right font-mono">{formatCurrency(h.marketValue)}</td>
                      <td className={`py-2 px-3 text-right font-mono ${h.gainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {h.gainLoss >= 0 ? "+" : ""}{formatCurrency(h.gainLoss)} ({h.gainLossPercent.toFixed(2)}%)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-4">No holdings yet.</p>
          )}
        </CardContent>
      </Card>

      {/* Trade Funds Form */}
      <Card>
        <CardHeader><CardTitle>Trade Funds</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleTradeSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Action</Label>
              <div className="flex gap-4">
                {["Buy", "Sell"].map((a) => (
                  <div key={a} className="flex items-center space-x-2">
                    <input type="radio" id={`trade-${a}`} checked={tradeForm.action === a} onChange={() => setTradeForm({ ...tradeForm, action: a })} />
                    <Label htmlFor={`trade-${a}`} className="cursor-pointer flex items-center gap-1">
                      {a === "Buy" ? <TrendingUp className="h-4 w-4 text-green-600" /> : <TrendingDown className="h-4 w-4 text-red-600" />} {a}
                    </Label>
                  </div>
                ))}
              </div>
              {tradeErrors.action && <p className="text-sm text-destructive">{tradeErrors.action}</p>}
            </div>

            <div className="space-y-2">
              <Label>Fund Symbol</Label>
              <Input placeholder="Search funds..." value={symbolFilter} onChange={(e) => setSymbolFilter(e.target.value)} className="mb-2" />
              <Select onValueChange={(v) => setTradeForm({ ...tradeForm, symbol: v })}>
                <SelectTrigger className={tradeErrors.symbol ? "border-destructive" : ""}><SelectValue placeholder="Select fund" /></SelectTrigger>
                <SelectContent>
                  {filteredFunds.map((f) => (
                    <SelectItem key={f.symbol} value={f.symbol}>{f.symbol} — {f.name} ({formatCurrency(f.price)})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {tradeErrors.symbol && <p className="text-sm text-destructive">{tradeErrors.symbol}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="tradeQty">Quantity</Label>
              <Input id="tradeQty" type="number" step="0.01" min="0.01" value={tradeForm.quantity} onChange={(e) => setTradeForm({ ...tradeForm, quantity: e.target.value })} placeholder="0" className={tradeErrors.quantity ? "border-destructive" : ""} />
              {tradeErrors.quantity && <p className="text-sm text-destructive">{tradeErrors.quantity}</p>}
            </div>

            <div className="space-y-2">
              <Label>{tradeForm.action === "Sell" ? "Destination Account" : "Funding Account"}</Label>
              <Select onValueChange={(v) => setTradeForm({ ...tradeForm, accountId: v })}>
                <SelectTrigger className={tradeErrors.accountId ? "border-destructive" : ""}><SelectValue placeholder="Select account" /></SelectTrigger>
                <SelectContent>
                  {accounts.map((a) => (<SelectItem key={a.id} value={a.id}>{a.name} — {formatCurrency(a.balance)}</SelectItem>))}
                </SelectContent>
              </Select>
              {tradeErrors.accountId && <p className="text-sm text-destructive">{tradeErrors.accountId}</p>}
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isTrading}>
              {isTrading ? "Executing Trade..." : "Execute Trade"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Recurring Investment Plan Form */}
      <Card>
        <CardHeader><CardTitle>Recurring Investment Plan</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handlePlanSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Fund Symbol</Label>
              <Select onValueChange={(v) => setPlanForm({ ...planForm, symbol: v })}>
                <SelectTrigger className={planErrors.symbol ? "border-destructive" : ""}><SelectValue placeholder="Select fund" /></SelectTrigger>
                <SelectContent>
                  {funds.map((f) => (<SelectItem key={f.symbol} value={f.symbol}>{f.symbol} — {f.name}</SelectItem>))}
                </SelectContent>
              </Select>
              {planErrors.symbol && <p className="text-sm text-destructive">{planErrors.symbol}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="contribution">Contribution Amount</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
                <Input id="contribution" type="number" step="1" min="25" value={planForm.contributionAmount} onChange={(e) => setPlanForm({ ...planForm, contributionAmount: e.target.value })} placeholder="25.00" className={`pl-8 ${planErrors.contributionAmount ? "border-destructive" : ""}`} />
              </div>
              {planErrors.contributionAmount && <p className="text-sm text-destructive">{planErrors.contributionAmount}</p>}
            </div>

            <div className="space-y-2">
              <Label>Frequency</Label>
              <div className="flex gap-4">
                {["Weekly", "Monthly"].map((f) => (
                  <div key={f} className="flex items-center space-x-2">
                    <input type="radio" id={`freq-${f}`} checked={planForm.frequency === f} onChange={() => setPlanForm({ ...planForm, frequency: f })} />
                    <Label htmlFor={`freq-${f}`} className="cursor-pointer">{f}</Label>
                  </div>
                ))}
              </div>
              {planErrors.frequency && <p className="text-sm text-destructive">{planErrors.frequency}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="planStartDate">Start Date</Label>
              <Input id="planStartDate" type="date" value={planForm.startDate} onChange={(e) => setPlanForm({ ...planForm, startDate: e.target.value })} className={planErrors.startDate ? "border-destructive" : ""} />
              {planErrors.startDate && <p className="text-sm text-destructive">{planErrors.startDate}</p>}
            </div>

            <div className="space-y-2">
              <Label>Funding Account</Label>
              <Select onValueChange={(v) => setPlanForm({ ...planForm, fundingAccountId: v })}>
                <SelectTrigger className={planErrors.fundingAccountId ? "border-destructive" : ""}><SelectValue placeholder="Select account" /></SelectTrigger>
                <SelectContent>
                  {accounts.map((a) => (<SelectItem key={a.id} value={a.id}>{a.name} — {formatCurrency(a.balance)}</SelectItem>))}
                </SelectContent>
              </Select>
              {planErrors.fundingAccountId && <p className="text-sm text-destructive">{planErrors.fundingAccountId}</p>}
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isCreatingPlan}>
              {isCreatingPlan ? "Creating Plan..." : "Create Plan"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
