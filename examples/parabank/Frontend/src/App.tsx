import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Transfer from "./pages/Transfer";
import OpenAccount from "./pages/OpenAccount";
import BillPay from "./pages/BillPay";
import RequestLoan from "./pages/RequestLoan";
import UpdateContactInfo from "./pages/UpdateContactInfo";
import ManageCards from "./pages/ManageCards";
import Investments from "./pages/Investments";
import AccountStatements from "./pages/AccountStatements";
import SecuritySettings from "./pages/SecuritySettings";
import SupportCenter from "./pages/SupportCenter";
import Layout from "./components/Layout";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes with Layout */}
          <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          <Route path="/transfer" element={<Layout><Transfer /></Layout>} />
          <Route path="/open-account" element={<Layout><OpenAccount /></Layout>} />
          <Route path="/bill-pay" element={<Layout><BillPay /></Layout>} />
          <Route path="/loan" element={<Layout><RequestLoan /></Layout>} />
          <Route path="/profile" element={<Layout><UpdateContactInfo /></Layout>} />
          <Route path="/cards" element={<Layout><ManageCards /></Layout>} />
          <Route path="/investments" element={<Layout><Investments /></Layout>} />
          <Route path="/statements" element={<Layout><AccountStatements /></Layout>} />
          <Route path="/security" element={<Layout><SecuritySettings /></Layout>} />
          <Route path="/support" element={<Layout><SupportCenter /></Layout>} />
          
          {/* Catch-all route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
