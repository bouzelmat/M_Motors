import React from "react";
import { Navigate, Outlet } from "react-router-dom";
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

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (requiredRole && user?.role !== requiredRole) {
        return <Navigate to="/dashboard" replace />;
    }

    return children ? <>{children}</> : <Outlet />;
};