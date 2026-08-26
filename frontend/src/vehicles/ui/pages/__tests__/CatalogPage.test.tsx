import type { ReactNode } from "react";

import type { UseQueryResult } from "@tanstack/react-query";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import {
    beforeEach,
    describe,
    expect,
    it,
    vi,
} from "vitest";

import { useVehiclesQuery } from "../../../application/hooks/useVehiclesQuery";
import { useVehicleFilterStore } from "../../../application/stores/useVehicleFilterStore";
import type { VehicleListItemDTO } from "../../../infrastructure/vehicle.types";
import { CatalogPage } from "../CatalogPage";

vi.mock("../../../application/hooks/useVehiclesQuery", () => ({
    useVehiclesQuery: vi.fn(),
}));

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
) {
    return render(
        <QueryClientProvider client={createQueryClient()}>
            {ui}
        </QueryClientProvider>,
    );
}

function createQueryResult(
    overrides: Partial<
        UseQueryResult<
            VehicleListItemDTO[],
            Error
        >
    >,
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

describe("CatalogPage", () => {
    beforeEach(() => {
        vi.clearAllMocks();

        useVehicleFilterStore.setState({
            mode: "rental",
            maxMonthlyRent: null,
        });
    });

    it("renders loading state", () => {
        mockedUseVehiclesQuery.mockReturnValue(
            createQueryResult({
                isLoading: true,
                isPending: true,
            }),
        );

        renderWithQueryClient(<CatalogPage />);

        expect(
            screen.getByRole("progressbar"),
        ).toBeInTheDocument();
    });

    it("renders error state", () => {
        mockedUseVehiclesQuery.mockReturnValue(
            createQueryResult({
                error: new Error("Network error"),
                isError: true,
                status: "error",
            }),
        );

        renderWithQueryClient(<CatalogPage />);

        expect(
            screen.getByText(
                /Une erreur est survenue lors du chargement du catalogue/i,
            ),
        ).toBeInTheDocument();
    });

    it("renders empty state when no vehicles are available", () => {
        mockedUseVehiclesQuery.mockReturnValue(
            createQueryResult({
                data: [],
                isSuccess: true,
                status: "success",
            }),
        );

        renderWithQueryClient(<CatalogPage />);

        expect(
            screen.getByText(
                /Aucun véhicule disponible pour le moment/i,
            ),
        ).toBeInTheDocument();
    });

    it("renders the vehicle list", () => {
        mockedUseVehiclesQuery.mockReturnValue(
            createQueryResult({
                data: mockVehicles,
                isSuccess: true,
                status: "success",
            }),
        );

        renderWithQueryClient(<CatalogPage />);

        expect(
            screen.getByText("Peugeot 208"),
        ).toBeInTheDocument();

        expect(
            screen.getByText("Renault Clio"),
        ).toBeInTheDocument();
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

        expect(
            useVehicleFilterStore.getState().mode,
        ).toBe("sale");
    });
});