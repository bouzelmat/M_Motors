import { createBrowserRouter } from "react-router-dom";

import App from "../App";
import { CatalogPage } from "../vehicles/ui/pages/CatalogPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/catalogue",
    element: <CatalogPage />,
  },
]);