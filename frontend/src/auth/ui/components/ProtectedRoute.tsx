import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "../hooks/useAuth";

interface ProtectedRouteProps {
    requiredRole?: string;
    children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    requiredRole,
    children,
}) => {
    const { isAuthenticated, user } = useAuthStore();
    const location = useLocation();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    if (requiredRole && user?.role !== requiredRole) {
        return <Navigate to={user?.role === "ADMIN" ? "/admin/dossiers" : "/dashboard"} replace />;
    }

    return children ? <>{children}</> : <Outlet />;
};