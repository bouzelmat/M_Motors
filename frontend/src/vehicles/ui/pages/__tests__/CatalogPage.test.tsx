import type { ReactNode } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  act,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import type { UseQueryResult } from "@tanstack/react-query";

import { useVehiclesQuery } from "../../../application/hooks/useVehiclesQuery";
import { useVehicleFilterStore } from "../../../application/stores/useVehicleFilterStore";
import type { VehicleListItemDTO } from "../../../infrastructure/vehicle.types";
import { CatalogPage } from "../CatalogPage";

vi.mock(
  "../../../application/hooks/useVehiclesQuery",
  () => ({
    useVehiclesQuery: vi.fn(),
  }),
);

const mockedUseVehiclesQuery = vi.mocked(useVehiclesQuery);

const mockVehicles: VehicleListItemDTO[] = [
  {
    id: "1",
    brand: "Peugeot",
    model: "208",
    year: 2023,
    monthly_rent: "350.00",
    photo_url: null,
    included_services: [],
  },
  {
    id: "2",
    brand: "Renault",
    model: "Clio",
    year: 2022,
    monthly_rent: "400.00",
    photo_url: null,
    included_services: [],
  },
];

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
}

function renderWithQueryClient(
  ui: ReactNode,
  initialEntry = "/",
) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <QueryClientProvider client={createQueryClient()}>
        {ui}
      </QueryClientProvider>
    </MemoryRouter>,
  );
}

function createQueryResult(
  overrides: Partial<UseQueryResult<VehicleListItemDTO[], Error>>,
): UseQueryResult<VehicleListItemDTO[], Error> {
  return {
    data: undefined,
    error: null,
    failureCount: 0,
    failureReason: null,
    errorUpdateCount: 0,
    isError: false,
    isFetched: true,
    isFetchedAfterMount: true,
    isFetching: false,
    isLoading: false,
    isLoadingError: false,
    isPending: false,
    isPlaceholderData: false,
    isRefetchError: false,
    isRefetching: false,
    isStale: false,
    isSuccess: false,
    status: "pending",
    fetchStatus: "idle",
    dataUpdatedAt: 0,
    errorUpdatedAt: 0,
    refetch: vi.fn(),
    promise: Promise.resolve(undefined),
    isEnabled: true,
    ...overrides,
  } as UseQueryResult<VehicleListItemDTO[], Error>;
}

describe("CatalogPage with FilterBar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    useVehicleFilterStore.setState({
      mode: "rental",
      maxMonthlyRent: null,
      brand: null,
      maxPrice: null,
      maxMileage: null,
      fuelType: null,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders loading state", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        isLoading: true,
        isPending: true,
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("renders error state", () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    const refetch = vi.fn();
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        error: new Error("Network error"),
        isError: true,
        status: "error",
        refetch,
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    expect(
      screen.getByText(
        /Une erreur est survenue lors du chargement du catalogue/i,
      ),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /réessayer/i }));
    expect(refetch).toHaveBeenCalledOnce();
    expect(consoleError).toHaveBeenCalledWith(
      "Erreur lors du chargement du catalogue :",
      expect.any(Error),
    );
    consoleError.mockRestore();
  });

  it("normalizes the purchase URL mode to sale", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: [],
        isSuccess: true,
        status: "success",
      }),
    );

    renderWithQueryClient(<CatalogPage />, "/catalogue?mode=purchase");

    expect(useVehicleFilterStore.getState().mode).toBe("sale");
    expect(mockedUseVehiclesQuery).toHaveBeenLastCalledWith(
      expect.objectContaining({ mode: "sale" }),
    );
  });

  it("renders the vehicle list when data is available", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: mockVehicles,
        isSuccess: true,
        status: "success",
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    expect(screen.getByText("Peugeot 208")).toBeInTheDocument();
    expect(screen.getByText("Renault Clio")).toBeInTheDocument();
  });

  it("changes the catalog mode when clicking the toggle button", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: [],
        isSuccess: true,
        status: "success",
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    fireEvent.click(
      screen.getByRole("button", {
        name: /achat/i,
      }),
    );

    expect(useVehicleFilterStore.getState().mode).toBe("sale");
  });

  it("updates store after debounce when typing in brand field", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: mockVehicles,
        isSuccess: true,
        status: "success",
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    const brandInput = screen.getByLabelText(/filtrer par marque/i);

    fireEvent.change(brandInput, { target: { value: "Peugeot" } });

    // Immédiatement : le store n'est pas encore mis à jour (debounce en cours)
    expect(useVehicleFilterStore.getState().brand).toBeNull();

    // Avance de 300ms pour déclencher le timer
    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(useVehicleFilterStore.getState().brand).toBe("Peugeot");
  });

  it("updates store after debounce when typing max price and max mileage", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: mockVehicles,
        isSuccess: true,
        status: "success",
      }),
    );

    useVehicleFilterStore.setState({ mode: "sale" });

    renderWithQueryClient(<CatalogPage />);

    const priceInput = screen.getByLabelText(/filtrer par budget max/i);
    const mileageInput = screen.getByLabelText(/filtrer par kilométrage max/i);

    fireEvent.change(priceInput, { target: { value: "25000" } });
    fireEvent.change(mileageInput, { target: { value: "60000" } });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(useVehicleFilterStore.getState().maxPrice).toBe(25000);
    expect(useVehicleFilterStore.getState().maxMileage).toBe(60000);
  });

  it("updates store immediately when selecting a fuel type", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: mockVehicles,
        isSuccess: true,
        status: "success",
      }),
    );

    renderWithQueryClient(<CatalogPage />);

    const selectCombobox = screen.getByLabelText(/filtrer par motorisation/i);
    fireEvent.mouseDown(selectCombobox);

    const optionElectric = screen.getByRole("option", { name: /électrique/i });
    fireEvent.click(optionElectric);

    expect(useVehicleFilterStore.getState().fuelType).toBe("ELECTRIQUE");
  });

  it("resets all filters when clicking the Reset button in FilterBar", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: mockVehicles,
        isSuccess: true,
        status: "success",
      }),
    );

    useVehicleFilterStore.setState({
      brand: "BMW",
      maxPrice: 40000,
      fuelType: "DIESEL",
    });

    renderWithQueryClient(<CatalogPage />);

    const resetButton = screen.getByRole("button", { name: /réinitialiser/i });
    fireEvent.click(resetButton);

    const state = useVehicleFilterStore.getState();
    expect(state.brand).toBeNull();
    expect(state.maxPrice).toBeNull();
    expect(state.fuelType).toBeNull();
  });

  it("displays empty state and resets filters when clicking 'Modifier mes filtres'", () => {
    mockedUseVehiclesQuery.mockReturnValue(
      createQueryResult({
        data: [],
        isSuccess: true,
        status: "success",
      }),
    );

    useVehicleFilterStore.setState({ brand: "Tesla" });

    renderWithQueryClient(<CatalogPage />);

    expect(
      screen.getByText(/aucun véhicule disponible à la location/i),
    ).toBeInTheDocument();

    const modifyButton = screen.getByRole("button", {
      name: /modifier mes filtres/i,
    });

    fireEvent.click(modifyButton);

    expect(useVehicleFilterStore.getState().brand).toBeNull();
  });
});