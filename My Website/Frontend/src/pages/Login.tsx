import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Building2, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { apiLogin, saveUser } from "@/lib/api";

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const res = await apiLogin(formData.username, formData.password);
      saveUser(res.user);
      toast({
        title: "Signed in successfully",
        description: "Welcome back to ParaBank",
      });
      navigate("/dashboard");
    } catch (err: any) {
      toast({
        title: "Sign in failed",
        description: err.message || "Incorrect email or password. Please try again.",
        variant: "destructive",
      });
      setFormData({ ...formData, password: "" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Building2 className="h-12 w-12 text-primary" />
            <span className="text-3xl font-bold text-foreground">ParaBank</span>
          </div>
          <p className="text-muted-foreground">Your trusted banking partner</p>
        </div>

        {/* Login Form */}
        <Card className="shadow-lg border-0 bg-card/80 backdrop-blur">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold">Sign In</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Email/Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="Enter your email or username"
                  className="bg-background/50"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    className="bg-background/50 pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-primary hover:bg-primary-hover"
                disabled={isLoading}
              >
                {isLoading ? "Signing In..." : "Sign In"}
              </Button>
            </form>

            <div className="mt-6 text-center space-y-4">
              <Link
                to="/forgot-password"
                className="text-sm text-primary hover:text-primary-hover transition-colors"
              >
                Forgot Password?
              </Link>
              
              <div className="text-sm text-muted-foreground">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="text-primary hover:text-primary-hover font-medium transition-colors"
                >
                  Register here
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Demo credentials */}
        <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/20">
          <p className="text-sm text-center font-semibold text-primary mb-2">Demo Credentials</p>
          <div className="text-center space-y-1">
            <p className="text-sm font-mono bg-background/80 px-3 py-1 rounded">
              <span className="text-muted-foreground">Email:</span> <span className="font-semibold">admin@parabank.com</span>
            </p>
            <p className="text-sm font-mono bg-background/80 px-3 py-1 rounded">
              <span className="text-muted-foreground">Username:</span> <span className="font-semibold">admin</span>
            </p>
            <p className="text-sm font-mono bg-background/80 px-3 py-1 rounded">
              <span className="text-muted-foreground">Password:</span> <span className="font-semibold">Admin123!@#</span>
            </p>
          </div>
          <p className="text-xs text-center text-muted-foreground mt-2">
            You can login using either email or username with the password above
          </p>
        </div>
      </div>
    </div>
  );
}