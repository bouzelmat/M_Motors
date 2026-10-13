import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DossiersClient } from "../../../infrastructure/DossiersClient";
import { useDossierDetail } from "../useDossierDetail";
import { useDossierStatus } from "../useDossierStatus";
import { useDossierHistory } from "../useDossierHistory";
import { useCreateDossier, useSubmitDossier, useValidateDossier, useRejectDossier, useRequestDocuments } from "../useDossierMutations";

vi.mock("../../../infrastructure/DossiersClient", async () => {
  const actual = await vi.importActual<typeof import("../../../infrastructure/DossiersClient")>("../../../infrastructure/DossiersClient");
  return { ...actual, DossiersClient: {
    createDossier: vi.fn(), submitDossier: vi.fn(), validateDossier: vi.fn(), rejectDossier: vi.fn(), requestDocuments: vi.fn(),
    getDossierDetail: vi.fn(), getDossierStatus: vi.fn(), getDossierHistory: vi.fn(),
  }};
});

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("hooks dossiers", () => {
  beforeEach(() => vi.clearAllMocks());

  it("charge le détail, le statut et l'historique", async () => {
    vi.mocked(DossiersClient.getDossierDetail).mockResolvedValue({ id: "d1" } as never);
    vi.mocked(DossiersClient.getDossierStatus).mockResolvedValue({ status: "SUBMITTED" } as never);
    vi.mocked(DossiersClient.getDossierHistory).mockResolvedValue([{ id: "d2" }] as never);
    const detail = renderHook(() => useDossierDetail("d1"), { wrapper });
    const status = renderHook(() => useDossierStatus("d1"), { wrapper });
    const history = renderHook(() => useDossierHistory(), { wrapper });
    await waitFor(() => expect(detail.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(status.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(history.result.current.isSuccess).toBe(true));
    expect(detail.result.current.data).toMatchObject({ id: "d1" });
    expect(status.result.current.data?.status).toBe("SUBMITTED");
    expect(history.result.current.data).toHaveLength(1);
  });

  it("reste désactivé si aucun identifiant n'est fourni", () => {
    const detail = renderHook(() => useDossierDetail(undefined), { wrapper });
    const status = renderHook(() => useDossierStatus(null), { wrapper });
    expect(detail.result.current.fetchStatus).toBe("idle");
    expect(status.result.current.fetchStatus).toBe("idle");
    expect(DossiersClient.getDossierDetail).not.toHaveBeenCalled();
  });

  it("exécute les mutations de création et d'administration", async () => {
    vi.mocked(DossiersClient.createDossier).mockResolvedValue({ id: "d1" } as never);
    vi.mocked(DossiersClient.submitDossier).mockResolvedValue({ id: "d1" } as never);
    vi.mocked(DossiersClient.validateDossier).mockResolvedValue({ status: "VALIDATED" } as never);
    vi.mocked(DossiersClient.rejectDossier).mockResolvedValue({ status: "REJECTED" } as never);
    vi.mocked(DossiersClient.requestDocuments).mockResolvedValue({ status: "DOCUMENTS_PENDING" } as never);
    const create = renderHook(() => useCreateDossier(), { wrapper });
    const submit = renderHook(() => useSubmitDossier("d1"), { wrapper });
    const validate = renderHook(() => useValidateDossier("d1"), { wrapper });
    const reject = renderHook(() => useRejectDossier("d1"), { wrapper });
    const request = renderHook(() => useRequestDocuments("d1"), { wrapper });
    await act(async () => {
      await create.result.current.mutateAsync({ vehicle_id: "v1", trade_in: null, financing_plan: null });
      await submit.result.current.mutateAsync();
      await validate.result.current.mutateAsync("ok");
      await reject.result.current.mutateAsync("non");
      await request.result.current.mutateAsync(["PAYSLIP"]);
    });
    expect(DossiersClient.createDossier).toHaveBeenCalled();
    expect(DossiersClient.submitDossier).toHaveBeenCalledWith("d1");
    expect(DossiersClient.validateDossier).toHaveBeenCalledWith("d1", "ok");
    expect(DossiersClient.rejectDossier).toHaveBeenCalledWith("d1", "non");
    expect(DossiersClient.requestDocuments).toHaveBeenCalledWith("d1", ["PAYSLIP"]);
  });
});
