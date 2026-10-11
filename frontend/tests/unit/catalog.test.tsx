import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { theme } from "../../src/shared/ui/theme/theme";
import { CatalogPage } from "../../src/vehicles/ui/pages/CatalogPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderWithProviders = (ui: React.ReactNode) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{ui}</BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe("Catalogue et Filtres (Ticket 4)", () => {
  it("renders catalog title and filters sidebar", () => {
    renderWithProviders(<CatalogPage />);
    expect(screen.getByText("Catalogue des Véhicules")).toBeInTheDocument();
  });
});
