import { useState, useEffect } from "react";
import { ArrowLeftRight, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { apiGetAccounts, apiTransfer, getUser } from "@/lib/api";

interface TransferAccount {
  id: string;
  name: string;
  balance: number;
}

export default function Transfer() {
  const [transferAccounts, setTransferAccounts] = useState<TransferAccount[]>([]);
  const user = getUser();

  useEffect(() => {
    if (!user) return;
    apiGetAccounts(user.id).then((accounts) => {
      setTransferAccounts(
        accounts
          .filter((a) => a.type === "Checking" || a.type === "Savings")
          .map((a) => ({ id: a.id, name: `${a.type} Account (${a.accountNumber})`, balance: a.balance }))
      );
    });
  }, []);

  const [formData, setFormData] = useState({
    amount: "",
    fromAccount: "",
    toAccount: "",
    toAccountConfirm: "",
    isExternal: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = "Please enter a valid transfer amount";
    }

    if (!formData.fromAccount) {
      newErrors.fromAccount = "Please select a source account";
    }

    if (!formData.toAccount) {
      newErrors.toAccount = "Please select or enter a destination account";
    }

    if (formData.isExternal && formData.toAccount !== formData.toAccountConfirm) {
      newErrors.toAccountConfirm = "Account numbers do not match";
    }

    if (formData.fromAccount === formData.toAccount && !formData.isExternal) {
      newErrors.toAccount = "Source and destination accounts cannot be the same";
    }

    const sourceAccount = transferAccounts.find(acc => acc.id === formData.fromAccount);
    if (sourceAccount && parseFloat(formData.amount) > sourceAccount.balance) {
      newErrors.amount = "Insufficient funds in source account";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const res = await apiTransfer({
        userId: user!.id,
        amount: parseFloat(formData.amount),
        fromAccountId: formData.fromAccount,
        toAccountId: formData.isExternal ? undefined : formData.toAccount,
        transferType: formData.isExternal ? "external" : "internal",
        externalAccountNumber: formData.isExternal ? formData.toAccount : undefined,
      });
      toast({
        title: "Transfer completed successfully",
        description: `Transaction ID: ${res.transactionId}`,
      });
      setFormData({ amount: "", fromAccount: "", toAccount: "", toAccountConfirm: "", isExternal: false });
      // Refresh account balances
      const accounts = await apiGetAccounts(user!.id);
      setTransferAccounts(
        accounts
          .filter((a) => a.type === "Checking" || a.type === "Savings")
          .map((a) => ({ id: a.id, name: `${a.type} Account (${a.accountNumber})`, balance: a.balance }))
      );
    } catch (err: any) {
      toast({ title: "Transfer failed", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: "",
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const selectedAccount = transferAccounts.find(acc => acc.id === formData.fromAccount);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <ArrowLeftRight className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Transfer Funds</h1>
        <p className="text-muted-foreground">Move money between your accounts or to external accounts</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transfer Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Transfer Amount */}
            <div className="space-y-2">
              <Label htmlFor="amount">Transfer Amount</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="amount"
                  name="amount"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={formData.amount}
                  onChange={handleInputChange}
                  placeholder="0.00"
                  className={`pl-8 ${errors.amount ? "border-destructive" : ""}`}
                />
              </div>
              {errors.amount && (
                <p className="text-sm text-destructive">{errors.amount}</p>
              )}
            </div>

            {/* Source Account */}
            <div className="space-y-2">
              <Label htmlFor="fromAccount">From Account</Label>
              <Select onValueChange={(value) => setFormData({ ...formData, fromAccount: value })}>
                <SelectTrigger className={errors.fromAccount ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select source account" />
                </SelectTrigger>
                <SelectContent>
                  {transferAccounts.map((account) => (
                    <SelectItem key={account.id} value={account.id}>
                      <div className="flex justify-between items-center w-full">
                        <span>{account.name}</span>
                        <span className="text-muted-foreground ml-4">
                          {formatCurrency(account.balance)}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.fromAccount && (
                <p className="text-sm text-destructive">{errors.fromAccount}</p>
              )}
              {selectedAccount && (
                <p className="text-sm text-muted-foreground">
                  Available balance: {formatCurrency(selectedAccount.balance)}
                </p>
              )}
            </div>

            {/* Transfer Type */}
            <div className="space-y-4">
              <Label>Transfer To</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    id="internal"
                    name="transferType"
                    checked={!formData.isExternal}
                    onChange={() => setFormData({ ...formData, isExternal: false, toAccount: "", toAccountConfirm: "" })}
                    className="text-primary"
                  />
                  <Label htmlFor="internal" className="cursor-pointer">My ParaBank Account</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    id="external"
                    name="transferType"
                    checked={formData.isExternal}
                    onChange={() => setFormData({ ...formData, isExternal: true, toAccount: "", toAccountConfirm: "" })}
                    className="text-primary"
                  />
                  <Label htmlFor="external" className="cursor-pointer">External Account</Label>
                </div>
              </div>
            </div>

            {/* Destination Account */}
            {!formData.isExternal ? (
              <div className="space-y-2">
                <Label htmlFor="toAccount">To Account</Label>
                <Select onValueChange={(value) => setFormData({ ...formData, toAccount: value })}>
                  <SelectTrigger className={errors.toAccount ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select destination account" />
                  </SelectTrigger>
                  <SelectContent>
                    {transferAccounts
                      .filter(account => account.id !== formData.fromAccount)
                      .map((account) => (
                      <SelectItem key={account.id} value={account.id}>
                        <div className="flex justify-between items-center w-full">
                          <span>{account.name}</span>
                          <span className="text-muted-foreground ml-4">
                            {formatCurrency(account.balance)}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.toAccount && (
                  <p className="text-sm text-destructive">{errors.toAccount}</p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="toAccount">External Account Number</Label>
                  <Input
                    id="toAccount"
                    name="toAccount"
                    required
                    value={formData.toAccount}
                    onChange={handleInputChange}
                    placeholder="Enter account number"
                    className={errors.toAccount ? "border-destructive" : ""}
                  />
                  {errors.toAccount && (
                    <p className="text-sm text-destructive">{errors.toAccount}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="toAccountConfirm">Confirm Account Number</Label>
                  <Input
                    id="toAccountConfirm"
                    name="toAccountConfirm"
                    required
                    value={formData.toAccountConfirm}
                    onChange={handleInputChange}
                    placeholder="Re-enter account number"
                    className={errors.toAccountConfirm ? "border-destructive" : ""}
                  />
                  {errors.toAccountConfirm && (
                    <p className="text-sm text-destructive">{errors.toAccountConfirm}</p>
                  )}
                </div>

                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    External transfers may take 1-3 business days to process and may incur fees.
                  </AlertDescription>
                </Alert>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover"
              disabled={isLoading}
            >
              {isLoading ? "Processing Transfer..." : "Transfer Funds"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Transfer Summary */}
      {formData.amount && formData.fromAccount && formData.toAccount && (
        <Card>
          <CardHeader>
            <CardTitle>Transfer Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Amount:</span>
                <span className="font-semibold">{formatCurrency(parseFloat(formData.amount) || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">From:</span>
                <span>{transferAccounts.find(acc => acc.id === formData.fromAccount)?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">To:</span>
                <span>
                  {formData.isExternal 
                    ? `External Account (****${formData.toAccount.slice(-4)})`
                    : transferAccounts.find(acc => acc.id === formData.toAccount)?.name
                  }
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Processing Time:</span>
                <span>{formData.isExternal ? "1-3 business days" : "Immediate"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Fee:</span>
                <span>{formData.isExternal ? "$3.00" : "Free"}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}