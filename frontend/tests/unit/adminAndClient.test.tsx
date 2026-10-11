import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { theme } from "../../src/shared/ui/theme/theme";
import { DossierTimeline } from "../../src/dossiers/ui/components/DossierTimeline";

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

describe("Espace Client & Admin (Ticket 7)", () => {
  it("renders status timeline steps for BROUILLON and VALIDÉ", () => {
    renderWithProviders(<DossierTimeline status="SUBMITTED" />);
    expect(screen.getByText("BROUILLON")).toBeInTheDocument();
    expect(screen.getByText("SOUMIS")).toBeInTheDocument();
    expect(screen.getByText("VALIDÉ")).toBeInTheDocument();
  });
});
