import { useState } from "react";
import { Shield, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useToast } from "@/hooks/use-toast";
import { apiChangePassword, getUser } from "@/lib/api";

export default function SecuritySettings() {
  const [isOpen, setIsOpen] = useState(true);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const user = getUser();
  const { toast } = useToast();

  const validatePassword = (pw: string): string | null => {
    if (pw.length < 8) return "At least 8 characters required";
    if (!/[A-Z]/.test(pw)) return "Must include an uppercase letter";
    if (!/[a-z]/.test(pw)) return "Must include a lowercase letter";
    if (!/\d/.test(pw)) return "Must include a digit";
    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(pw)) return "Must include a special character";
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!currentPassword) errs.currentPassword = "Current password is required";
    if (!newPassword) errs.newPassword = "New password is required";
    else {
      const pwErr = validatePassword(newPassword);
      if (pwErr) errs.newPassword = pwErr;
    }
    if (!confirmPassword) errs.confirmPassword = "Confirm password is required";
    else if (newPassword !== confirmPassword) errs.confirmPassword = "Passwords do not match";
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setIsSubmitting(true);
    try {
      const res = await apiChangePassword(user!.id, currentPassword, newPassword);
      toast({ title: res.message });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setErrors({});
    } catch (err: any) {
      if (err.message.includes("incorrect")) {
        setErrors({ currentPassword: err.message });
      } else {
        toast({ title: "Error", description: err.message, variant: "destructive" });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const pwStrength = (() => {
    if (!newPassword) return { label: "", color: "" };
    let score = 0;
    if (newPassword.length >= 8) score++;
    if (/[A-Z]/.test(newPassword)) score++;
    if (/[a-z]/.test(newPassword)) score++;
    if (/\d/.test(newPassword)) score++;
    if (/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(newPassword)) score++;
    if (score <= 2) return { label: "Weak", color: "bg-red-500" };
    if (score <= 3) return { label: "Fair", color: "bg-yellow-500" };
    if (score <= 4) return { label: "Good", color: "bg-blue-500" };
    return { label: "Strong", color: "bg-green-500" };
  })();

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div className="text-center">
        <Shield className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Security Settings</h1>
        <p className="text-muted-foreground">Manage your account security</p>
      </div>

      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/30 transition-colors">
              <CardTitle className="flex items-center justify-between">
                Change Password
                <span className="text-sm font-normal text-muted-foreground">{isOpen ? "▲" : "▼"}</span>
              </CardTitle>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Current Password */}
                <div className="space-y-2">
                  <Label htmlFor="currentPw">Current Password</Label>
                  <div className="relative">
                    <Input
                      id="currentPw"
                      type={showCurrent ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className={errors.currentPassword ? "border-destructive pr-10" : "pr-10"}
                    />
                    <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" onClick={() => setShowCurrent(!showCurrent)}>
                      {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.currentPassword && <p className="text-sm text-destructive">{errors.currentPassword}</p>}
                </div>

                {/* New Password */}
                <div className="space-y-2">
                  <Label htmlFor="newPw">New Password</Label>
                  <div className="relative">
                    <Input
                      id="newPw"
                      type={showNew ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className={errors.newPassword ? "border-destructive pr-10" : "pr-10"}
                    />
                    <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" onClick={() => setShowNew(!showNew)}>
                      {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.newPassword && <p className="text-sm text-destructive">{errors.newPassword}</p>}
                  {newPassword && (
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div className={`h-full ${pwStrength.color} transition-all`} style={{ width: `${Math.max(20, (pwStrength.label === "Weak" ? 25 : pwStrength.label === "Fair" ? 50 : pwStrength.label === "Good" ? 75 : 100))}%` }} />
                        </div>
                        <span className="text-xs text-muted-foreground">{pwStrength.label}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Confirm New Password */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPw">Confirm New Password</Label>
                  <div className="relative">
                    <Input
                      id="confirmPw"
                      type={showConfirm ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className={errors.confirmPassword ? "border-destructive pr-10" : "pr-10"}
                    />
                    <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" onClick={() => setShowConfirm(!showConfirm)}>
                      {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.confirmPassword && <p className="text-sm text-destructive">{errors.confirmPassword}</p>}
                </div>

                <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isSubmitting}>
                  {isSubmitting ? "Changing Password..." : "Change Password"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  );
}
