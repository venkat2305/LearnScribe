import { useState } from "react";
import { Link, useLocation, Outlet } from "react-router-dom";
import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  Home,
  LogOut,
  Menu,
  Plus,
  Settings,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  isActive: boolean;
}

const SidebarItem = ({ icon, label, href, isActive }: SidebarItemProps) => (
  <Link to={href}>
    <Button
      variant="ghost"
      className={cn(
        "w-full justify-start gap-2 font-normal",
        isActive ? "bg-secondary text-secondary-foreground" : "hover:bg-secondary/50"
      )}
    >
      {icon}
      <span>{label}</span>
    </Button>
  </Link>
);

interface SidebarGroupProps {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

const SidebarGroup = ({ icon, label, children, defaultOpen = false }: SidebarGroupProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="space-y-1">
      <Button
        variant="ghost"
        className="w-full justify-start gap-2 font-normal"
        onClick={() => setIsOpen(!isOpen)}
      >
        {icon}
        <span className="flex-1 text-left">{label}</span>
        {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </Button>
      {isOpen && <div className="pl-6 space-y-1">{children}</div>}
    </div>
  );
};

interface SidebarLayoutProps {
  children: React.ReactNode;
}

export default function SidebarLayout({ children }: SidebarLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { logout } = useAuth();
  const location = useLocation();
  
  const handleLogout = () => {
    logout();
    toast.info("Logged out", {
      description: "You've been successfully logged out."
    });
  };

  const isPathActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile sidebar toggle */}
      <div className="fixed top-4 left-4 z-50 md:hidden">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          {isSidebarOpen ? <X size={18} /> : <Menu size={18} />}
        </Button>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed md:relative z-40 h-full w-64 flex-shrink-0 overflow-y-auto bg-card border-r border-border transition-transform duration-200 ease-in-out",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Sidebar header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-border">
            <Link to="/dashboard" className="font-bold text-xl">LearnScribe</Link>
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsSidebarOpen(false)}
            >
              <X size={18} />
            </Button>
          </div>
          
          {/* Sidebar content */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            <SidebarItem
              icon={<Home size={18} />}
              label="Dashboard"
              href="/dashboard"
              isActive={isPathActive("/dashboard")}
            />
            
            <SidebarGroup icon={<BookOpen size={18} />} label="Quizzes" defaultOpen>
              <SidebarItem
                icon={<Plus size={18} />}
                label="Create Quiz"
                href="/quiz/create"
                isActive={isPathActive("/quiz/create")}
              />
              <SidebarItem
                icon={<BookOpen size={18} />}
                label="My Quizzes"
                href="/quiz/myquizzes"
                isActive={isPathActive("/quiz/myquizzes")}
              />
            </SidebarGroup>
            
            {/* <SidebarGroup icon={<BookOpen size={18} />} label="Summaries" defaultOpen>
              <SidebarItem
                icon={<Plus size={18} />}
                label="Create Summary"
                href="/summary/create"
                isActive={isPathActive("/summary/create")}
              />
              <SidebarItem
                icon={<BookOpen size={18} />}
                label="My Summaries"
                href="/summary/mysummaries"
                isActive={isPathActive("/summary/mysummaries")}
              />
            </SidebarGroup> */}
          </div>
          
          {/* Sidebar footer */}
          <div className="p-3 border-t border-border">
            <SidebarItem 
              icon={<Settings size={18} />}
              label="Settings"
              href="/settings"
              isActive={isPathActive("/settings")}
            />
            <Button
              variant="ghost"
              className="w-full justify-start gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
              onClick={handleLogout}
            >
              <LogOut size={18} />
              <span>Logout</span>
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className={cn(
        "flex-1 overflow-x-hidden overflow-y-auto bg-background p-6",
        !isSidebarOpen && "md:ml-0"
      )}>
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}