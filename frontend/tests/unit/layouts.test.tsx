import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { theme } from "../../src/shared/ui/theme/theme";
import { Navbar } from "../../src/shared/ui/layout/Navbar";
import { Footer } from "../../src/shared/ui/layout/Footer";
import { PublicLayout } from "../../src/shared/ui/layout/PublicLayout";

const renderWithProviders = (ui: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>{ui}</BrowserRouter>
    </ThemeProvider>
  );
};

describe("Layouts & Navigation (Ticket 2)", () => {
  it("renders Navbar brand title and navigation links", () => {
    renderWithProviders(<Navbar />);
    expect(screen.getByText("M-MOTORS")).toBeInTheDocument();
    expect(screen.getByText("Catalogue")).toBeInTheDocument();
  });

  it("renders Footer with copyright and legal links", () => {
    renderWithProviders(<Footer />);
    expect(screen.getByText(/La plateforme automobile nouvelle génération/)).toBeInTheDocument();
  });

  it("renders PublicLayout container correctly", () => {
    renderWithProviders(<PublicLayout />);
    expect(screen.getAllByText("M-MOTORS").length).toBeGreaterThan(0);
  });

});
