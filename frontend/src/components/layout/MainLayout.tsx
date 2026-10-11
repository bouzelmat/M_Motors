import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import { PublicLayout } from "../../shared/ui/layout/PublicLayout";
import { AdminLayout } from "../../shared/ui/layout/AdminLayout";
import { useAuthStore } from "../../auth/ui/hooks/useAuth";

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const { user } = useAuthStore();
  const isAdminPath = location.pathname.startsWith("/admin");
  const isStaff = user?.role === "ADMIN";

  if (isAdminPath || isStaff) {
    return <AdminLayout />;
  }

  return <PublicLayout />;
};

export default MainLayout;