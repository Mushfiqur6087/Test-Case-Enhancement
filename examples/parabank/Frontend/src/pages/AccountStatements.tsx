import { useState, useEffect } from "react";
import { FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { apiGetAccounts, apiGenerateStatement, apiGetStatementPrefs, apiSaveStatementPrefs, getUser } from "@/lib/api";

interface StatementTx {
  id: string; description: string; amount: number; date: string; type: string; category: string; transactionId: string;
}
interface Account { id: string; accountNumber: string; type: string; balance: number; }

export default function AccountStatements() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const user = getUser();
  const { toast } = useToast();

  // Generate statement form
  const [stmtForm, setStmtForm] = useState({ accountId: "", startDate: "", endDate: "" });
  const [stmtErrors, setStmtErrors] = useState<Record<string, string>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [statementData, setStatementData] = useState<StatementTx[] | null>(null);

  // e-statement prefs form
  const [paperless, setPaperless] = useState(false);
  const [prefEmail, setPrefEmail] = useState("");
  const [prefError, setPrefError] = useState("");
  const [isSavingPref, setIsSavingPref] = useState(false);

  useEffect(() => {
    if (!user) return;
    const load = async () => {
      try {
        const [accts, prefs] = await Promise.all([
          apiGetAccounts(user.id),
          apiGetStatementPrefs(user.id),
        ]);
        setAccounts(accts);
        setPaperless(prefs.paperless);
        setPrefEmail(prefs.email || "");
      } catch (err) { console.error(err); }
    };
    load();
  }, []);

  const formatCurrency = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!stmtForm.accountId) errs.accountId = "Select an account";
    if (!stmtForm.startDate) errs.startDate = "Start date is required";
    if (!stmtForm.endDate) errs.endDate = "End date is required";
    if (stmtForm.startDate && stmtForm.endDate && stmtForm.startDate > stmtForm.endDate) {
      errs.endDate = "End date must be after start date";
    }
    setStmtErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsGenerating(true);
    setStatementData(null);
    try {
      const res = await apiGenerateStatement(user!.id, stmtForm.accountId, stmtForm.startDate, stmtForm.endDate);
      setStatementData(res.transactions);
      toast({ title: res.message });
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Unable to generate statement — please try again later.", variant: "destructive" });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSavePref = async (e: React.FormEvent) => {
    e.preventDefault();
    setPrefError("");
    if (paperless && !prefEmail) {
      setPrefError("Email is required for paperless statements");
      return;
    }
    if (prefEmail) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(prefEmail)) {
        setPrefError("Invalid email address");
        return;
      }
    }

    setIsSavingPref(true);
    try {
      const res = await apiSaveStatementPrefs(user!.id, paperless, prefEmail);
      toast({ title: res.message });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    } finally {
      setIsSavingPref(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Account Statements</h1>
        <p className="text-muted-foreground">Generate statements and manage e-statement preferences</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Generate Statement */}
        <Card>
          <CardHeader><CardTitle>Generate Statement</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="space-y-2">
                <Label>Account</Label>
                <Select onValueChange={(v) => setStmtForm({ ...stmtForm, accountId: v })}>
                  <SelectTrigger className={stmtErrors.accountId ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select account" />
                  </SelectTrigger>
                  <SelectContent>
                    {accounts.map((a) => (
                      <SelectItem key={a.id} value={a.id}>{a.type} ({a.accountNumber})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {stmtErrors.accountId && <p className="text-sm text-destructive">{stmtErrors.accountId}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input id="startDate" type="date" value={stmtForm.startDate} onChange={(e) => setStmtForm({ ...stmtForm, startDate: e.target.value })} className={stmtErrors.startDate ? "border-destructive" : ""} />
                {stmtErrors.startDate && <p className="text-sm text-destructive">{stmtErrors.startDate}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">End Date</Label>
                <Input id="endDate" type="date" value={stmtForm.endDate} onChange={(e) => setStmtForm({ ...stmtForm, endDate: e.target.value })} className={stmtErrors.endDate ? "border-destructive" : ""} />
                {stmtErrors.endDate && <p className="text-sm text-destructive">{stmtErrors.endDate}</p>}
              </div>
              <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isGenerating}>
                {isGenerating ? "Generating..." : "Generate Statement"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* e-Statement Preferences */}
        <Card>
          <CardHeader><CardTitle>e-Statement Preferences</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSavePref} className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox id="paperless" checked={paperless} onCheckedChange={(v) => setPaperless(!!v)} />
                <Label htmlFor="paperless" className="cursor-pointer">Opt into paperless statements</Label>
              </div>
              <div className="space-y-2">
                <Label htmlFor="prefEmail">Email Address</Label>
                <Input id="prefEmail" type="email" value={prefEmail} onChange={(e) => setPrefEmail(e.target.value)} placeholder="you@example.com" className={prefError ? "border-destructive" : ""} />
                {prefError && <p className="text-sm text-destructive">{prefError}</p>}
              </div>
              <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isSavingPref}>
                {isSavingPref ? "Saving..." : "Save Preference"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Statement Results */}
      {statementData !== null && (
        <Card>
          <CardHeader><CardTitle>Statement Results ({statementData.length} transactions)</CardTitle></CardHeader>
          <CardContent>
            {statementData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-3">Date</th>
                      <th className="text-left py-2 px-3">Description</th>
                      <th className="text-left py-2 px-3">Type</th>
                      <th className="text-left py-2 px-3">Category</th>
                      <th className="text-right py-2 px-3">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statementData.map((tx) => (
                      <tr key={tx.id} className="border-b">
                        <td className="py-2 px-3">{new Date(tx.date).toLocaleDateString()}</td>
                        <td className="py-2 px-3">{tx.description}</td>
                        <td className="py-2 px-3"><span className={`inline-block px-2 py-0.5 rounded text-xs ${tx.type === "credit" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{tx.type}</span></td>
                        <td className="py-2 px-3 text-muted-foreground">{tx.category}</td>
                        <td className={`py-2 px-3 text-right font-mono ${tx.type === "credit" ? "text-green-600" : "text-red-600"}`}>
                          {tx.type === "credit" ? "+" : "-"}{formatCurrency(Math.abs(tx.amount))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-4">No transactions found for the selected period.</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
