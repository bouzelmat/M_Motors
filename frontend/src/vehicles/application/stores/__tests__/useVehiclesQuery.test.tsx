import type { ReactNode } from "react";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { vehiclesClient } from "../../../infrastructure/VehiclesClient";
import { useVehiclesQuery } from "../../hooks/useVehiclesQuery";

vi.mock("../../../infrastructure/VehiclesClient", () => ({
  vehiclesClient: {
    getCatalog: vi.fn(),
  },
}));

const mockedGetCatalog = vi.mocked(vehiclesClient.getCatalog);

const MODE_RENTAL = "rental";
const MODE_SALE = "sale";

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        retryDelay: 0,
      },
    },
  });
}

function createWrapper() {
  const queryClient = createQueryClient();

  return function Wrapper({
    children,
  }: {
    children: ReactNode;
  }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe("useVehiclesQuery", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should fetch vehicles with the provided filters", async () => {
    const mockData = [
      {
        id: "1",
        brand: "Peugeot",
        model: "208",
        year: 2023,
        monthly_rent: "350.00",
        photo_url: null,
        included_services: [],
      },
    ];

    mockedGetCatalog.mockResolvedValueOnce(mockData);

    const { result } = renderHook(
      () =>
        useVehiclesQuery({
          mode: MODE_RENTAL,
          maxMonthlyRent: 350,
        }),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(mockedGetCatalog).toHaveBeenCalledTimes(1);

    expect(mockedGetCatalog).toHaveBeenCalledWith({
      mode: MODE_RENTAL,
      max_monthly_rent: 350,
    });

    expect(result.current.data).toEqual(mockData);
  });

  it("should omit maxMonthlyRent when it is null", async () => {
    mockedGetCatalog.mockResolvedValueOnce([]);

    const { result } = renderHook(
      () =>
        useVehiclesQuery({
          mode: MODE_SALE,
          maxMonthlyRent: null,
        }),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(mockedGetCatalog).toHaveBeenCalledWith({
      mode: MODE_SALE,
      max_monthly_rent: undefined,
    });
  });

  it("should expose the loading state while the request is pending", () => {
    mockedGetCatalog.mockImplementation(
      () => new Promise(() => {}),
    );

    const { result } = renderHook(
      () =>
        useVehiclesQuery({
          mode: MODE_RENTAL,
        }),
      {
        wrapper: createWrapper(),
      },
    );

    expect(result.current.isLoading).toBe(true);
    expect(result.current.isSuccess).toBe(false);
  });

  it("should expose the error state when the request fails", async () => {
    const error = new Error("Network error");

    mockedGetCatalog.mockRejectedValue(error);

    const { result } = renderHook(
      () =>
        useVehiclesQuery({
          mode: MODE_RENTAL,
        }),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBe(error);
  });
});