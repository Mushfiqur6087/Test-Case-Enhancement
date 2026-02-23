import { useState } from "react";
import { Link, useLocation, Outlet, useNavigate } from "react-router-dom";
import { 
  Home, 
  PlusCircle, 
  ArrowLeftRight, 
  CreditCard, 
  Banknote, 
  User, 
  Settings, 
  BarChart3, 
  FileText, 
  Shield, 
  HelpCircle, 
  LogOut,
  Building2,
  Menu,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { clearUser, getUser } from "@/lib/api";

const navigation = [
  { name: "Accounts Overview", href: "/dashboard", icon: Home },
  { name: "Open New Account", href: "/open-account", icon: PlusCircle },
  { name: "Transfer Funds", href: "/transfer", icon: ArrowLeftRight },
  { name: "Bill Pay", href: "/bill-pay", icon: CreditCard },
  { name: "Request Loan", href: "/loan", icon: Banknote },
  { name: "Update Contact Info", href: "/profile", icon: User },
  { name: "Manage Cards", href: "/cards", icon: CreditCard },
  { name: "Investments", href: "/investments", icon: BarChart3 },
  { name: "Account Statements", href: "/statements", icon: FileText },
  { name: "Security Settings", href: "/security", icon: Shield },
  { name: "Support Center", href: "/support", icon: HelpCircle },
];

interface LayoutProps {
  children?: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const user = getUser();

  const handleLogout = () => {
    clearUser();
    
    // Show logout confirmation
    toast({
      title: "Logged out successfully",
      description: "You have been safely logged out of ParaBank",
    });
    
    // Redirect to login page
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-200 ease-in-out md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-border">
            <div className="flex items-center gap-2">
              <Building2 className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold text-foreground">ParaBank</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-4 py-6">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <item.icon className="h-5 w-5" />
                      {item.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-border">
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-muted-foreground hover:text-destructive"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
              Log Out
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between bg-card border-b border-border px-6">
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">Welcome back, {user ? `${user.firstName} ${user.lastName}` : "Guest"}</span>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
}