import { ReactNode } from "react";
import SidebarLayout from "../components/layout/Sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return <SidebarLayout>{children}</SidebarLayout>;
}