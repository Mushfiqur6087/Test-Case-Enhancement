import { useState, useEffect } from "react";
import { User, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { apiGetUser, apiUpdateUser, getUser } from "@/lib/api";

const states = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
];

export default function UpdateContactInfo() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    streetAddress: "",
    city: "",
    state: "",
    zipCode: "",
    phoneNumber: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const { toast } = useToast();
  const user = getUser();

  useEffect(() => {
    if (!user) return;
    apiGetUser(user.id)
      .then((data) => {
        setFormData({
          firstName: data.firstName || "",
          lastName: data.lastName || "",
          streetAddress: data.streetAddress || "",
          city: data.city || "",
          state: data.state || "",
          zipCode: data.zipCode || "",
          phoneNumber: data.phoneNumber || "",
        });
      })
      .catch(() => {
        toast({ title: "Failed to load profile", variant: "destructive" });
      })
      .finally(() => setLoadingProfile(false));
  }, []);

  const formatPhoneNumber = (value: string) => {
    const phoneNumber = value.replace(/[^\d]/g, "");
    if (phoneNumber.length < 4) return phoneNumber;
    if (phoneNumber.length < 7) return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.firstName.trim()) newErrors.firstName = "First name is required";
    if (!formData.lastName.trim()) newErrors.lastName = "Last name is required";
    if (!formData.streetAddress.trim()) newErrors.streetAddress = "Street address is required";
    if (!formData.city.trim()) newErrors.city = "City is required";
    if (!formData.state) newErrors.state = "State is required";
    if (!formData.zipCode.trim()) newErrors.zipCode = "ZIP code is required";

    const zipRegex = /^\d{5}(-\d{4})?$/;
    if (formData.zipCode && !zipRegex.test(formData.zipCode)) {
      newErrors.zipCode = "Please enter a valid ZIP code";
    }

    if (formData.phoneNumber) {
      const phoneRegex = /^\(\d{3}\) \d{3}-\d{4}$/;
      if (!phoneRegex.test(formData.phoneNumber)) {
        newErrors.phoneNumber = "Phone must be in format (123) 456-7890";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      toast({ title: "Validation Error", description: "Please fix the errors below.", variant: "destructive" });
      return;
    }
    setIsLoading(true);
    try {
      await apiUpdateUser(user!.id, formData);
      toast({ title: "Profile updated successfully.", description: "Your contact information has been updated." });
      // Refresh data
      const data = await apiGetUser(user!.id);
      setFormData({
        firstName: data.firstName || "",
        lastName: data.lastName || "",
        streetAddress: data.streetAddress || "",
        city: data.city || "",
        state: data.state || "",
        zipCode: data.zipCode || "",
        phoneNumber: data.phoneNumber || "",
      });
    } catch (err: any) {
      toast({ title: "Update failed", description: err.message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: "" });
  };

  if (loadingProfile) {
    return <div className="text-center py-12"><p className="text-muted-foreground">Loading profile...</p></div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <User className="h-12 w-12 text-primary mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-foreground">Update Contact Info</h1>
        <p className="text-muted-foreground">Keep your personal information up to date</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input id="firstName" name="firstName" required value={formData.firstName} onChange={handleInputChange} className={errors.firstName ? "border-destructive" : ""} />
                {errors.firstName && <p className="text-sm text-destructive">{errors.firstName}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input id="lastName" name="lastName" required value={formData.lastName} onChange={handleInputChange} className={errors.lastName ? "border-destructive" : ""} />
                {errors.lastName && <p className="text-sm text-destructive">{errors.lastName}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="streetAddress">Street Address</Label>
              <Input id="streetAddress" name="streetAddress" required value={formData.streetAddress} onChange={handleInputChange} className={errors.streetAddress ? "border-destructive" : ""} />
              {errors.streetAddress && <p className="text-sm text-destructive">{errors.streetAddress}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="city">City</Label>
                <Input id="city" name="city" required value={formData.city} onChange={handleInputChange} className={errors.city ? "border-destructive" : ""} />
                {errors.city && <p className="text-sm text-destructive">{errors.city}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Select onValueChange={(value) => { setFormData({ ...formData, state: value }); if (errors.state) setErrors({ ...errors, state: "" }); }} value={formData.state}>
                  <SelectTrigger className={errors.state ? "border-destructive" : ""}><SelectValue placeholder="Select state" /></SelectTrigger>
                  <SelectContent>{states.map((s) => (<SelectItem key={s} value={s}>{s}</SelectItem>))}</SelectContent>
                </Select>
                {errors.state && <p className="text-sm text-destructive">{errors.state}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="zipCode">ZIP Code</Label>
                <Input id="zipCode" name="zipCode" required value={formData.zipCode} onChange={handleInputChange} placeholder="12345" className={errors.zipCode ? "border-destructive" : ""} />
                {errors.zipCode && <p className="text-sm text-destructive">{errors.zipCode}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phoneNumber">Phone Number</Label>
              <Input id="phoneNumber" name="phoneNumber" value={formData.phoneNumber} onChange={(e) => { const formatted = formatPhoneNumber(e.target.value); setFormData({ ...formData, phoneNumber: formatted }); if (errors.phoneNumber) setErrors({ ...errors, phoneNumber: "" }); }} placeholder="(123) 456-7890" className={errors.phoneNumber ? "border-destructive" : ""} />
              {errors.phoneNumber && <p className="text-sm text-destructive">{errors.phoneNumber}</p>}
            </div>

            {Object.keys(errors).length > 0 && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>Please correct the highlighted fields before submitting.</AlertDescription>
              </Alert>
            )}

            <Button type="submit" className="w-full bg-primary hover:bg-primary-hover" disabled={isLoading}>
              {isLoading ? "Updating Profile..." : "Update Profile"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
