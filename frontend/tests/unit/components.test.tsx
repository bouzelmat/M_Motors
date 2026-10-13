import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { theme } from "../../src/shared/ui/theme/theme";
import { ModeBadge } from "../../src/vehicles/ui/components/ModeBadge";
import { StatusBadge } from "../../src/dossiers/ui/components/StatusBadge";
import { PriceTag } from "../../src/shared/ui/components/PriceTag";
import { SpecLine } from "../../src/vehicles/ui/components/SpecLine";
import { SectionHeading } from "../../src/shared/ui/components/SectionHeading";
import { VehicleCard } from "../../src/vehicles/ui/components/VehicleCard";

const renderWithTheme = (ui: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>{ui}</BrowserRouter>
    </ThemeProvider>
  );
};

describe("Atomic UI Components (Ticket 1)", () => {
  describe("ModeBadge", () => {
    it("renders ACHAT badge", () => {
      renderWithTheme(<ModeBadge mode="ACHAT" />);
      expect(screen.getByText("ACHAT")).toBeInTheDocument();
    });

    it("renders LOCATION LLD badge", () => {
      renderWithTheme(<ModeBadge mode="LOCATION" />);
      expect(screen.getByText("LOCATION LLD")).toBeInTheDocument();
    });
  });

  describe("StatusBadge", () => {
    it("renders BROUILLON status badge", () => {
      renderWithTheme(<StatusBadge status="BROUILLON" />);
      expect(screen.getByText("BROUILLON")).toBeInTheDocument();
    });

    it("renders VALIDÉ status badge", () => {
      renderWithTheme(<StatusBadge status="VALIDÉ" />);
      expect(screen.getByText("VALIDÉ")).toBeInTheDocument();
    });
  });

  describe("PriceTag", () => {
    it("formats EUR price correctly with Intl.NumberFormat", () => {
      renderWithTheme(<PriceTag price={24900} />);
      // 24 900 €
      expect(screen.getByText(/24\s?900\s?€/)).toBeInTheDocument();
    });

    it("displays /mois when isMonthly is true", () => {
      renderWithTheme(<PriceTag price={349} isMonthly />);
      expect(screen.getByText(/349\s?€/)).toBeInTheDocument();
      expect(screen.getByText("/mois")).toBeInTheDocument();
    });
  });

  describe("SpecLine", () => {
    it("renders compact specs line", () => {
      renderWithTheme(<SpecLine year={2021} mileage={45000} fuelType="Diesel" />);
      expect(screen.getByText(/2021 • 45\s?000 km • Diesel/)).toBeInTheDocument();
    });
  });

  describe("SectionHeading", () => {
    it("renders eyebrow, title and subtitle", () => {
      renderWithTheme(
        <SectionHeading eyebrow="EXCLUSIVITÉ" title="Notre Sélection" subtitle="Découvrez nos meilleures offres" />
      );
      expect(screen.getByText("EXCLUSIVITÉ")).toBeInTheDocument();
      expect(screen.getByText("Notre Sélection")).toBeInTheDocument();
      expect(screen.getByText("Découvrez nos meilleures offres")).toBeInTheDocument();
    });
  });

  describe("VehicleCard", () => {
    it("renders vehicle card with specs, brand, model and price", () => {
      renderWithTheme(
        <VehicleCard
          id="v1"
          brand="Tesla"
          model="Model 3"
          year={2023}
          mileage={12000}
          fuelType="Électrique"
          price={499}
          mode="LOCATION"
        />
      );
      expect(screen.getAllByText(/Tesla/).length).toBeGreaterThan(0);
      expect(screen.getByText(/Model 3/)).toBeInTheDocument();
      expect(screen.getByText("LOCATION LLD")).toBeInTheDocument();
      expect(screen.getByText(/499\s?€/)).toBeInTheDocument();
    });
  });
});