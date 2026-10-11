import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { theme } from "../../src/shared/ui/theme/theme";
import { NewDossierPage } from "../../src/dossiers/ui/pages/NewDossierPage";

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

describe("Tunnel de Souscription (Ticket 6)", () => {
  it("renders Stepper steps and custom summary component", () => {
    renderWithProviders(<NewDossierPage />);
    expect(screen.getByText("Configuration & Offre")).toBeInTheDocument();
    expect(screen.getByText("Justificatifs")).toBeInTheDocument();
  });
});
