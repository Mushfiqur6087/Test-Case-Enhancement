import { useState, useEffect } from "react";
import { CreditCard, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { apiGetAccounts, apiGetCards, apiRequestCard, apiUpdateCardControls, getUser, type CardInfo } from "@/lib/api";

interface LinkableAccount {
  id: string;
  name: string;
  balance: number;
}

export default function ManageCards() {
  const [accounts, setAccounts] = useState<LinkableAccount[]>([]);
  const [cards, setCards] = useState<CardInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const user = getUser();
  const { toast } = useToast();

  // Request Card form
  const [requestForm, setRequestForm] = useState({
    cardType: "",
    linkedAccountId: "",
    shippingAddress: "",
  });
  const [requestErrors, setRequestErrors] = useState<Record<string, string>>({});

  // Card Controls form
  const [controlsForm, setControlsForm] = useState({
    selectedCard: "",
    spendingLimit: "",
    travelNoticeStart: "",
    travelNoticeEnd: "",
    travelNoticeDestination: "",
    status: "",
  });
  const [controlsErrors, setControlsErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!user) return;
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [accts, c] = await Promise.all([apiGetAccounts(user!.id), apiGetCards(user!.id)]);
      setAccounts(
        accts
          .filter((a) => a.status === "Active")
          .map((a) => ({ id: a.id, name: `${a.type} Account (${a.accountNumber})`, balance: a.balance }))
      );
      setCards(c);
    } catch (err) {
      console.error("Failed to load data", err);
    }
  };

  // When a card is selected, populate controls
  useEffect(() => {
    if (controlsForm.selectedCard) {
      const card = cards.find((c) => c.id === controlsForm.selectedCard);
      if (card) {
        setControlsForm({
          ...controlsForm,
          spendingLimit: card.spendingLimit?.toString() || "",
          travelNoticeStart: card.travelNoticeStart || "",
          travelNoticeEnd: card.travelNoticeEnd || "",
          travelNoticeDestination: card.travelNoticeDestination || "",
          status: card.status,
        });
      }
    }
  }, [controlsForm.selectedCard]);

  const validateRequestForm = () => {
    const newErrors: Record<string, string> = {};
    if (!requestForm.cardType) newErrors.cardType = "Please select a card type";
    if (!requestForm.linkedAccountId) newErrors.linkedAccountId = "Please select an account to link";
    if (!requestForm.shippingAddress.trim()) newErrors.shippingAddress = "Shipping address is required";
    setRequestErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRequestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateRequestForm()) return;
    setIsLoading(true);
    try {
      const res = await apiRequestCard({
        userId: user!.id,
        cardType: requestForm.cardType,
        linkedAccountId: requestForm.linkedAccountId,
        shippingAddress: requestForm.shippingAddress,
      });
      toast({ title: "Card request submitted successfully.", description: `Tracking ID: ${res.trackingId}` });
      setRequestForm({ cardType: "", linkedAccountId: "", shippingAddress: "" });
      await loadData();
    } catch (err: any) {
      toast({ title: "Card request failed", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const validateControlsForm = () => {
    const newErrors: Record<string, string> = {};
    if (!controlsForm.selectedCard) newErrors.selectedCard = "Please select a card";
    if (controlsForm.spendingLimit && (isNaN(Number(controlsForm.spendingLimit)) || Number(controlsForm.spendingLimit) < 0)) {
      newErrors.spendingLimit = "Spending limit must be a valid positive number";
    }
    if (controlsForm.spendingLimit && Number(controlsForm.spendingLimit) > 50000) {
      newErrors.spendingLimit = "Spending limit cannot exceed $50,000 (policy maximum)";
    }
    if (controlsForm.travelNoticeStart && controlsForm.travelNoticeEnd) {
      if (new Date(controlsForm.travelNoticeEnd) <= new Date(controlsForm.travelNoticeStart)) {
        newErrors.travelNoticeEnd = "End date must be after start date";
      }
    }
    setControlsErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleControlsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateControlsForm()) return;
    setIsUpdating(true);
    try {
      await apiUpdateCardControls(controlsForm.selectedCard, {
        userId: user!.id,
        spendingLimit: controlsForm.spendingLimit ? Number(controlsForm.spendingLimit) : undefined,
        travelNoticeStart: controlsForm.travelNoticeStart || undefined,
        travelNoticeEnd: controlsForm.travelNoticeEnd || undefined,
        travelNoticeDestination: controlsForm.travelNoticeDestination || undefined,
        status: controlsForm.status || undefined,
      });
      toast({ title: "Card controls updated successfully." });
      await loadData();
    } catch (err: any) {
      toast({ title: "Update failed", description: err.message, variant: "destructive" });
    } finally {
      setIsUpdating(false);
    }
  };

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <CreditCard className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Manage Cards</h1>
        <p className="text-muted-foreground">Request new cards and manage existing card controls</p>
      </div>

      {/* Existing Cards Overview */}
      {cards.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Your Cards</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {cards.map((card) => (
                <div key={card.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">{card.type} Card •••• {card.last4}</p>
                      <p className="text-sm text-muted-foreground">Expires {card.expiryDate} | Linked: {card.linkedAccountType} ({card.linkedAccountNumber})</p>
                    </div>
                  </div>
                  <Badge variant={card.status === "Active" ? "outline" : "destructive"} className={card.status === "Active" ? "text-green-600 border-green-600" : ""}>
                    {card.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Request New Card Form */}
      <Card>
        <CardHeader><CardTitle>Request New Card</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleRequestSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Card Type</Label>
              <div className="grid grid-cols-2 gap-4">
                {["Debit", "Credit"].map((type) => (
                  <Card
                    key={type}
                    className={`cursor-pointer transition-all border-2 ${requestForm.cardType === type ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"}`}
                    onClick={() => { setRequestForm({ ...requestForm, cardType: type }); if (requestErrors.cardType) setRequestErrors({ ...requestErrors, cardType: "" }); }}
                  >
                    <CardContent className="p-4 text-center">
                      <input type="radio" checked={requestForm.cardType === type} onChange={() => {}} className="mb-2" />
                      <p className="font-semibold">{type} Card</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
              {requestErrors.cardType && <p className="text-sm text-destructive">{requestErrors.cardType}</p>}
            </div>

            <div className="space-y-2">
              <Label>Account to Link</Label>
              <Select onValueChange={(value) => setRequestForm({ ...requestForm, linkedAccountId: value })}>
                <SelectTrigger className={requestErrors.linkedAccountId ? "border-destructive" : ""}><SelectValue placeholder="Select account" /></SelectTrigger>
                <SelectContent>
                  {accounts.map((a) => (
                    <SelectItem key={a.id} value={a.id}>{a.name} — {formatCurrency(a.balance)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {requestErrors.linkedAccountId && <p className="text-sm text-destructive">{requestErrors.linkedAccountId}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="shippingAddress">Shipping Address</Label>
              <Input id="shippingAddress" value={requestForm.shippingAddress} onChange={(e) => { setRequestForm({ ...requestForm, shippingAddress: e.target.value }); if (requestErrors.shippingAddress) setRequestErrors({ ...requestErrors, shippingAddress: "" }); }} placeholder="Enter full shipping address" className={requestErrors.shippingAddress ? "border-destructive" : ""} />
              {requestErrors.shippingAddress && <p className="text-sm text-destructive">{requestErrors.shippingAddress}</p>}
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isLoading}>
              {isLoading ? "Submitting Request..." : "Request Card"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Card Controls Form */}
      {cards.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Card Controls</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleControlsSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Select Existing Card</Label>
                <Select onValueChange={(value) => setControlsForm({ ...controlsForm, selectedCard: value })}>
                  <SelectTrigger className={controlsErrors.selectedCard ? "border-destructive" : ""}><SelectValue placeholder="Select card" /></SelectTrigger>
                  <SelectContent>
                    {cards.map((card) => (
                      <SelectItem key={card.id} value={card.id}>{card.type} Card •••• {card.last4}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {controlsErrors.selectedCard && <p className="text-sm text-destructive">{controlsErrors.selectedCard}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="spendingLimit">New Spending Limit</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
                  <Input id="spendingLimit" type="number" step="100" min="0" max="50000" value={controlsForm.spendingLimit} onChange={(e) => setControlsForm({ ...controlsForm, spendingLimit: e.target.value })} placeholder="0.00" className={`pl-8 ${controlsErrors.spendingLimit ? "border-destructive" : ""}`} />
                </div>
                {controlsErrors.spendingLimit && <p className="text-sm text-destructive">{controlsErrors.spendingLimit}</p>}
              </div>

              <div className="space-y-2">
                <Label>Travel Notice (optional)</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">Start Date</Label>
                    <Input type="date" value={controlsForm.travelNoticeStart} onChange={(e) => setControlsForm({ ...controlsForm, travelNoticeStart: e.target.value })} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">End Date</Label>
                    <Input type="date" value={controlsForm.travelNoticeEnd} onChange={(e) => setControlsForm({ ...controlsForm, travelNoticeEnd: e.target.value })} className={controlsErrors.travelNoticeEnd ? "border-destructive" : ""} />
                    {controlsErrors.travelNoticeEnd && <p className="text-sm text-destructive">{controlsErrors.travelNoticeEnd}</p>}
                  </div>
                </div>
                <Input placeholder="Destination (e.g., Europe, Asia)" value={controlsForm.travelNoticeDestination} onChange={(e) => setControlsForm({ ...controlsForm, travelNoticeDestination: e.target.value })} />
              </div>

              <div className="space-y-2">
                <Label>Card Status</Label>
                <div className="flex gap-4">
                  {["Active", "Frozen"].map((s) => (
                    <div key={s} className="flex items-center space-x-2">
                      <input type="radio" id={`status-${s}`} checked={controlsForm.status === s} onChange={() => setControlsForm({ ...controlsForm, status: s })} />
                      <Label htmlFor={`status-${s}`} className="cursor-pointer">{s}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isUpdating || !controlsForm.selectedCard}>
                {isUpdating ? "Updating Controls..." : "Update Controls"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
