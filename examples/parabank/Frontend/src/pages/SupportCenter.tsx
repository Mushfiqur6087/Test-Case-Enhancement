import { useState } from "react";
import { Headphones, MessageSquare, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { apiSendSupportMessage, apiRequestCallback, getUser } from "@/lib/api";

export default function SupportCenter() {
  const user = getUser();
  const { toast } = useToast();

  // Secure message form
  const [msgForm, setMsgForm] = useState({ subject: "", category: "", messageBody: "", attachmentName: "" });
  const [msgErrors, setMsgErrors] = useState<Record<string, string>>({});
  const [isSendingMsg, setIsSendingMsg] = useState(false);

  // Callback form
  const [cbForm, setCbForm] = useState({
    reason: "",
    preferredDate: "",
    preferredTimeWindow: "",
    phone: user?.phone || "",
  });
  const [cbErrors, setCbErrors] = useState<Record<string, string>>({});
  const [isRequestingCb, setIsRequestingCb] = useState(false);

  const handleMsgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!msgForm.subject || msgForm.subject.trim().length < 3) errs.subject = "Subject must be at least 3 characters";
    if (msgForm.subject && msgForm.subject.length > 200) errs.subject = "Subject must be 200 characters or fewer";
    if (!msgForm.category) errs.category = "Select a category";
    if (!msgForm.messageBody || msgForm.messageBody.trim().length === 0) errs.messageBody = "Message body is required";
    if (msgForm.attachmentName) {
      const allowed = [".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"];
      const ext = msgForm.attachmentName.substring(msgForm.attachmentName.lastIndexOf(".")).toLowerCase();
      if (!allowed.includes(ext)) errs.attachmentName = "Allowed: PDF, PNG, JPG, DOC, DOCX";
    }
    setMsgErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsSendingMsg(true);
    try {
      const res = await apiSendSupportMessage({
        userId: user!.id,
        subject: msgForm.subject,
        category: msgForm.category,
        messageBody: msgForm.messageBody,
        attachmentName: msgForm.attachmentName || undefined,
      });
      toast({ title: res.message, description: `Ticket ID: ${res.ticketId}` });
      setMsgForm({ subject: "", category: "", messageBody: "", attachmentName: "" });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    } finally {
      setIsSendingMsg(false);
    }
  };

  const handleCbSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!cbForm.reason) errs.reason = "Select a reason";
    if (!cbForm.preferredDate) errs.preferredDate = "Preferred date is required";
    else {
      const d = new Date(cbForm.preferredDate + "T00:00:00");
      const today = new Date(); today.setHours(0, 0, 0, 0);
      const nextBiz = new Date(today); nextBiz.setDate(nextBiz.getDate() + 1);
      while (nextBiz.getDay() === 0 || nextBiz.getDay() === 6) nextBiz.setDate(nextBiz.getDate() + 1);
      if (d < nextBiz) errs.preferredDate = "Date must be at least the next business day";
    }
    if (!cbForm.preferredTimeWindow) errs.preferredTimeWindow = "Select a time window";
    if (!cbForm.phone) errs.phone = "Phone number is required";
    else if (!/^\d{3}-\d{3}-\d{4}$/.test(cbForm.phone)) errs.phone = "Format: ###-###-####";
    setCbErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsRequestingCb(true);
    try {
      const res = await apiRequestCallback({
        userId: user!.id,
        reason: cbForm.reason,
        preferredDate: cbForm.preferredDate,
        preferredTimeWindow: cbForm.preferredTimeWindow,
        phone: cbForm.phone,
      });
      toast({ title: res.message });
      setCbForm({ reason: "", preferredDate: "", preferredTimeWindow: "", phone: user?.phone || "" });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    } finally {
      setIsRequestingCb(false);
    }
  };

  const categories = ["Account", "Technical", "Security", "Other"];
  const reasons = ["Account inquiry", "Transaction dispute", "Technical issue", "Card services", "Loan inquiry", "General question"];
  const timeWindows = ["Morning (9 AM – 12 PM)", "Afternoon (12 PM – 3 PM)", "Evening (3 PM – 6 PM)"];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="text-center">
        <Headphones className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Support Center</h1>
        <p className="text-muted-foreground">Send us a secure message or schedule a callback</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Secure Message Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><MessageSquare className="h-5 w-5" /> Secure Message</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleMsgSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="msgSubject">Subject</Label>
                <Input id="msgSubject" value={msgForm.subject} onChange={(e) => setMsgForm({ ...msgForm, subject: e.target.value })} placeholder="Brief description of your inquiry" className={msgErrors.subject ? "border-destructive" : ""} />
                {msgErrors.subject && <p className="text-sm text-destructive">{msgErrors.subject}</p>}
              </div>

              <div className="space-y-2">
                <Label>Category</Label>
                <Select onValueChange={(v) => setMsgForm({ ...msgForm, category: v })}>
                  <SelectTrigger className={msgErrors.category ? "border-destructive" : ""}><SelectValue placeholder="Select category" /></SelectTrigger>
                  <SelectContent>
                    {categories.map((c) => (<SelectItem key={c} value={c}>{c}</SelectItem>))}
                  </SelectContent>
                </Select>
                {msgErrors.category && <p className="text-sm text-destructive">{msgErrors.category}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="msgBody">Message Body</Label>
                <Textarea id="msgBody" value={msgForm.messageBody} onChange={(e) => setMsgForm({ ...msgForm, messageBody: e.target.value })} rows={5} placeholder="Describe your issue in detail..." className={msgErrors.messageBody ? "border-destructive" : ""} />
                {msgErrors.messageBody && <p className="text-sm text-destructive">{msgErrors.messageBody}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="attachment">Attachment (optional)</Label>
                <Input id="attachment" value={msgForm.attachmentName} onChange={(e) => setMsgForm({ ...msgForm, attachmentName: e.target.value })} placeholder="filename.pdf" />
                <p className="text-xs text-muted-foreground">Accepted: PDF, PNG, JPG, DOC, DOCX</p>
                {msgErrors.attachmentName && <p className="text-sm text-destructive">{msgErrors.attachmentName}</p>}
              </div>

              <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isSendingMsg}>
                {isSendingMsg ? "Sending..." : "Send Message"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Schedule Callback Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><PhoneCall className="h-5 w-5" /> Schedule Callback</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCbSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Reason for Call</Label>
                <Select onValueChange={(v) => setCbForm({ ...cbForm, reason: v })}>
                  <SelectTrigger className={cbErrors.reason ? "border-destructive" : ""}><SelectValue placeholder="Select reason" /></SelectTrigger>
                  <SelectContent>
                    {reasons.map((r) => (<SelectItem key={r} value={r}>{r}</SelectItem>))}
                  </SelectContent>
                </Select>
                {cbErrors.reason && <p className="text-sm text-destructive">{cbErrors.reason}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="cbDate">Preferred Date</Label>
                <Input id="cbDate" type="date" value={cbForm.preferredDate} onChange={(e) => setCbForm({ ...cbForm, preferredDate: e.target.value })} className={cbErrors.preferredDate ? "border-destructive" : ""} />
                {cbErrors.preferredDate && <p className="text-sm text-destructive">{cbErrors.preferredDate}</p>}
              </div>

              <div className="space-y-2">
                <Label>Preferred Time Window</Label>
                <Select onValueChange={(v) => setCbForm({ ...cbForm, preferredTimeWindow: v })}>
                  <SelectTrigger className={cbErrors.preferredTimeWindow ? "border-destructive" : ""}><SelectValue placeholder="Select time window" /></SelectTrigger>
                  <SelectContent>
                    {timeWindows.map((w) => (<SelectItem key={w} value={w}>{w}</SelectItem>))}
                  </SelectContent>
                </Select>
                {cbErrors.preferredTimeWindow && <p className="text-sm text-destructive">{cbErrors.preferredTimeWindow}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="cbPhone">Phone Number</Label>
                <Input id="cbPhone" value={cbForm.phone} onChange={(e) => setCbForm({ ...cbForm, phone: e.target.value })} placeholder="555-123-4567" className={cbErrors.phone ? "border-destructive" : ""} />
                {cbErrors.phone && <p className="text-sm text-destructive">{cbErrors.phone}</p>}
              </div>

              <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isRequestingCb}>
                {isRequestingCb ? "Submitting..." : "Request Callback"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
