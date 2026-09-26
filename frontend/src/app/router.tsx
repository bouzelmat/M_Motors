import { createBrowserRouter } from "react-router-dom";

import App from "../App";
import { LoginPage } from "../auth/ui/pages/LoginPage";
import { RegisterPage } from "../auth/ui/pages/RegisterPage";
import { ProtectedRoute } from "../auth/ui/components/ProtectedRoute";
import { DossiersPage } from "../dossiers/ui/pages/DossiersPage";
import { SubscriptionConfirmationPage } from "../dossiers/ui/pages/SubscriptionConfirmationPage";
import { AdminDossiersPage } from "../dossiers/ui/pages/AdminDossiersPage";
import { AdminDossierDetailPage } from "../dossiers/ui/pages/AdminDossierDetailPage";
import { CatalogPage } from "../vehicles/ui/pages/CatalogPage";
import { VehicleDetailPage } from "../vehicles/ui/pages/VehicleDetailPage";
import { AddVehiclePage } from "../vehicles/ui/pages/AddVehiclePage";
import { VehiclePhotoUploadPage } from "../vehicles/ui/pages/VehiclePhotoUploadPage";

export const router = createBrowserRouter([
	{
		path: "/",
		element: <App />,
	},
	{
		path: "/catalogue",
		element: <CatalogPage />,
	},
	{
		path: "/catalogue/:vehicleId",
		element: <VehicleDetailPage />,
	},
	{
		path: "/login",
		element: <LoginPage />,
	},
	{
		path: "/register",
		element: <RegisterPage />,
	},
	{
		path: "/dashboard",
		element: (
			<ProtectedRoute>
				<DossiersPage />
			</ProtectedRoute>
		),
	},
	{
		path: "/dossiers/confirmation",
		element: (
			<ProtectedRoute>
				<SubscriptionConfirmationPage />
			</ProtectedRoute>
		),
	},
	{
		path: "/admin/dossiers",
		element: (
			<ProtectedRoute requiredRole="ADMIN">
				<AdminDossiersPage />
			</ProtectedRoute>
		),
	},
	{
		path: "/admin/dossiers/:dossierId",
		element: (
			<ProtectedRoute requiredRole="ADMIN">
				<AdminDossierDetailPage />
			</ProtectedRoute>
		),
	},
	{
		path: "/admin/vehicles/new",
		element: (
			<ProtectedRoute requiredRole="ADMIN">
				<AddVehiclePage />
			</ProtectedRoute>
		),
	},
	{
		path: "/admin/vehicles/:vehicleId/photos",
		element: (
			<ProtectedRoute requiredRole="ADMIN">
				<VehiclePhotoUploadPage />
			</ProtectedRoute>
		),
	},
]);