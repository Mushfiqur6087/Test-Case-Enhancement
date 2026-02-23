import { useState, useEffect } from "react";
import { PlusCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { apiGetAccounts, apiOpenAccount, getUser } from "@/lib/api";

interface FundingAccount {
  id: string;
  name: string;
  balance: number;
}

export default function OpenAccount() {
  const [fundingAccounts, setFundingAccounts] = useState<FundingAccount[]>([]);
  const user = getUser();

  useEffect(() => {
    if (!user) return;
    apiGetAccounts(user.id).then((accounts) => {
      setFundingAccounts(
        accounts
          .filter((a) => a.type === "Checking" || a.type === "Savings")
          .map((a) => ({ id: a.id, name: `${a.type} Account (${a.accountNumber})`, balance: a.balance }))
      );
    });
  }, []);

  const accountTypes = [
    { type: "Checking", description: "For everyday transactions and bill payments", minimumDeposit: 25, features: ["No monthly fees", "Unlimited transactions", "Online banking", "Mobile app"] },
    { type: "Savings", description: "Earn interest on your savings", minimumDeposit: 100, features: ["2.5% APY", "No monthly fees", "Online banking", "Mobile app"] },
  ];

  const [formData, setFormData] = useState({
    accountType: "",
    initialDeposit: "",
    fundingAccount: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const selectedAccountType = accountTypes.find(type => type.type === formData.accountType);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.accountType) {
      newErrors.accountType = "Please select an account type";
    }

    if (!formData.initialDeposit || parseFloat(formData.initialDeposit) <= 0) {
      newErrors.initialDeposit = "Please enter a valid initial deposit amount";
    } else if (selectedAccountType && parseFloat(formData.initialDeposit) < selectedAccountType.minimumDeposit) {
      newErrors.initialDeposit = `Minimum deposit for ${selectedAccountType.type} account is $${selectedAccountType.minimumDeposit}`;
    }

    if (!formData.fundingAccount) {
      newErrors.fundingAccount = "Please select a funding source";
    }

    const fundingAccount = fundingAccounts.find(acc => acc.id === formData.fundingAccount);
    if (fundingAccount && parseFloat(formData.initialDeposit) > fundingAccount.balance) {
      newErrors.initialDeposit = "Insufficient funds in funding account";
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
      const res = await apiOpenAccount({
        userId: user!.id,
        type: formData.accountType,
        initialDeposit: parseFloat(formData.initialDeposit),
        fundingAccountId: formData.fundingAccount,
      });
      toast({
        title: "Account created successfully",
        description: `Your new ${res.account.type} account (${res.account.accountNumber}) has been created with a balance of $${formData.initialDeposit}`,
      });
      setFormData({ accountType: "", initialDeposit: "", fundingAccount: "" });
      // Refresh funding accounts
      const accounts = await apiGetAccounts(user!.id);
      setFundingAccounts(
        accounts
          .filter((a) => a.type === "Checking" || a.type === "Savings")
          .map((a) => ({ id: a.id, name: `${a.type} Account (${a.accountNumber})`, balance: a.balance }))
      );
    } catch (err: any) {
      toast({ title: "Account creation failed", description: err.message, variant: "destructive" });
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

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <PlusCircle className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Open New Account</h1>
        <p className="text-muted-foreground">Choose the account type that best fits your needs</p>
      </div>

      {/* Account Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {accountTypes.map((accountType) => (
          <Card 
            key={accountType.type}
            className={`cursor-pointer transition-all border-2 ${
              formData.accountType === accountType.type 
                ? "border-primary bg-primary/5" 
                : "border-border hover:border-primary/50"
            }`}
            onClick={() => setFormData({ ...formData, accountType: accountType.type })}
          >
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                {accountType.type}
                <input
                  type="radio"
                  checked={formData.accountType === accountType.type}
                  onChange={() => {}}
                  className="text-primary"
                />
              </CardTitle>
              <p className="text-sm text-muted-foreground">{accountType.description}</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm font-medium">
                  Minimum deposit: {formatCurrency(accountType.minimumDeposit)}
                </p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {accountType.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <span className="w-1 h-1 bg-primary rounded-full"></span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Account Opening Form */}
      <Card>
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Account Type (Hidden - selected above) */}
            <input type="hidden" name="accountType" value={formData.accountType} />

            {/* Initial Deposit */}
            <div className="space-y-2">
              <Label htmlFor="initialDeposit">Initial Deposit Amount</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="initialDeposit"
                  name="initialDeposit"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={formData.initialDeposit}
                  onChange={handleInputChange}
                  placeholder="0.00"
                  className={`pl-8 ${errors.initialDeposit ? "border-destructive" : ""}`}
                  disabled={!formData.accountType}
                />
              </div>
              {selectedAccountType && (
                <p className="text-sm text-muted-foreground">
                  Minimum deposit: {formatCurrency(selectedAccountType.minimumDeposit)}
                </p>
              )}
              {errors.initialDeposit && (
                <p className="text-sm text-destructive">{errors.initialDeposit}</p>
              )}
            </div>

            {/* Funding Source */}
            <div className="space-y-2">
              <Label htmlFor="fundingAccount">Funding Source Account</Label>
              <Select 
                onValueChange={(value) => setFormData({ ...formData, fundingAccount: value })}
                disabled={!formData.accountType}
              >
                <SelectTrigger className={errors.fundingAccount ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select funding source" />
                </SelectTrigger>
                <SelectContent>
                  {fundingAccounts.map((account) => (
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
              {errors.fundingAccount && (
                <p className="text-sm text-destructive">{errors.fundingAccount}</p>
              )}
            </div>

            {/* Important Information */}
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Your new account will be opened immediately and funds will be transferred from your selected funding source.
                You will receive email confirmation once the account is active.
              </AlertDescription>
            </Alert>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover"
              disabled={isLoading || !formData.accountType}
            >
              {isLoading ? "Opening Account..." : "Open Account"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Account Summary */}
      {formData.accountType && formData.initialDeposit && formData.fundingAccount && (
        <Card>
          <CardHeader>
            <CardTitle>Account Opening Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Account Type:</span>
                <span className="font-semibold">{formData.accountType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Initial Deposit:</span>
                <span className="font-semibold">{formatCurrency(parseFloat(formData.initialDeposit) || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Funding Source:</span>
                <span>{fundingAccounts.find(acc => acc.id === formData.fundingAccount)?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Processing Time:</span>
                <span>Immediate</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Monthly Fee:</span>
                <span className="text-success">$0.00</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}