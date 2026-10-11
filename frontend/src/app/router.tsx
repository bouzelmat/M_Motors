import { createBrowserRouter, Navigate } from "react-router-dom";

import { HomePage } from "./HomePage";
import { LoginPage } from "../auth/ui/pages/LoginPage";
import { RegisterPage } from "../auth/ui/pages/RegisterPage";
import { ProtectedRoute } from "../auth/ui/components/ProtectedRoute";
import { DossiersPage } from "../dossiers/ui/pages/DossiersPage";
import { SubscriptionConfirmationPage } from "../dossiers/ui/pages/SubscriptionConfirmationPage";
import { AdminDossiersPage } from "../dossiers/ui/pages/AdminDossiersPage";
import { AdminDossierDetailPage } from "../dossiers/ui/pages/AdminDossierDetailPage";
import { CatalogPage } from "../vehicles/ui/pages/CatalogPage";
import { VehicleDetailPage } from "../vehicles/ui/pages/VehicleDetailPage";
import { VehicleSlugPage } from "../vehicles/ui/pages/VehicleSlugPage";
import { AddVehiclePage } from "../vehicles/ui/pages/AddVehiclePage";
import { AdminVehiclesPage } from "../vehicles/ui/pages/AdminVehiclesPage";
import { EditVehiclePage } from "../vehicles/ui/pages/EditVehiclePage";
import { VehiclePhotoUploadPage } from "../vehicles/ui/pages/VehiclePhotoUploadPage";
import { SimulatorPage } from "../vehicles/ui/pages/SimulatorPage";
import { NewDossierPage } from "../dossiers/ui/pages/NewDossierPage";
import { AccountDossierPage } from "../dossiers/ui/pages/AccountDossierPage";
import { MainLayout } from "../components/layout/MainLayout";

export const router = createBrowserRouter([
	{
		path: "/",
		element: <MainLayout />,
		children: [
			{ index: true, element: <HomePage /> },
			{ path: "vehicles", element: <Navigate to="/catalogue" replace /> },
			{ path: "simulator", element: <SimulatorPage /> },
			{ path: "simulateur-lld", element: <Navigate to="/#mini-simulateur" replace /> },
			{ path: "comment-ca-marche", element: <Navigate to="/#process-title" replace /> },
			{ path: "catalogue", element: <CatalogPage /> },
			{ path: "catalogue/:vehicleId", element: <VehicleDetailPage /> },
			{ path: "vehicles/:vehicleId", element: <VehicleSlugPage /> },
			{ path: "login", element: <LoginPage /> },
			{ path: "register", element: <RegisterPage /> },
			{
				path: "profil",
				element: <ProtectedRoute><Navigate to="/dashboard" replace /></ProtectedRoute>,
			},
			{
				path: "dossiers/new",
				element: <ProtectedRoute requiredRole="CLIENT"><NewDossierPage /></ProtectedRoute>,
			},
			{
				path: "account/dossiers/:dossierId",
				element: <ProtectedRoute requiredRole="CLIENT"><AccountDossierPage /></ProtectedRoute>,
			},
			{
				path: "dashboard",
				element: <ProtectedRoute requiredRole="CLIENT"><DossiersPage /></ProtectedRoute>,
			},
			{
				path: "dossiers/confirmation",
				element: <ProtectedRoute requiredRole="CLIENT"><SubscriptionConfirmationPage /></ProtectedRoute>,
			},
			{
				path: "admin/dossiers",
				element: <ProtectedRoute requiredRole="ADMIN"><AdminDossiersPage /></ProtectedRoute>,
			},
			{
				path: "admin/dossiers/:dossierId",
				element: <ProtectedRoute requiredRole="ADMIN"><AdminDossierDetailPage /></ProtectedRoute>,
			},
			{
				path: "admin/vehicles",
				element: <ProtectedRoute requiredRole="ADMIN"><AdminVehiclesPage /></ProtectedRoute>,
			},
			{
				path: "admin/vehicles/new",
				element: <ProtectedRoute requiredRole="ADMIN"><AddVehiclePage /></ProtectedRoute>,
			},
			{
				path: "admin/vehicles/:vehicleId/edit",
				element: <ProtectedRoute requiredRole="ADMIN"><EditVehiclePage /></ProtectedRoute>,
			},
			{
				path: "admin/vehicles/:vehicleId/photos",
				element: <ProtectedRoute requiredRole="ADMIN"><VehiclePhotoUploadPage /></ProtectedRoute>,
			},
			{ path: "*", element: <Navigate to="/" replace /> },
		],
	},
]);