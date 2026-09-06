import { createBrowserRouter } from "react-router-dom";

import App from "../App";
import { CatalogPage } from "../vehicles/ui/pages/CatalogPage";
import { VehicleDetailPage } from "../vehicles/ui/pages/VehicleDetailPage";

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
]);
