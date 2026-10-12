import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../..//shared/infrastructure/http/apiClient";
import { DossiersClient } from "../DossiersClient";

vi.mock("../../../shared/infrastructure/http/apiClient", () => ({
  apiClient: { get: vi.fn(), post: vi.fn() },
}));

describe("DossiersClient", () => {
  const get = vi.mocked(apiClient.get);
  const post = vi.mocked(apiClient.post);

  beforeEach(() => vi.clearAllMocks());

  it("crée, soumet et annule un dossier", async () => {
    post
      .mockResolvedValueOnce({ data: { id: "d1", vehicle_id: "v1", status: "DRAFT" } } as never)
      .mockResolvedValueOnce({ data: { id: "d1", vehicle_id: "v1", status: "SUBMITTED" } } as never)
      .mockResolvedValueOnce({ data: { id: "d1", vehicle_id: "v1", status: "CANCELLED" } } as never);
    const request = { vehicle_id: "v1", trade_in: null, financing_plan: null };
    expect(await DossiersClient.createDossier(request)).toMatchObject({ id: "d1" });
    expect(await DossiersClient.submitDossier("d1")).toMatchObject({ status: "SUBMITTED" });
    expect(await DossiersClient.cancelDossier("d1")).toMatchObject({ status: "CANCELLED" });
    expect(post).toHaveBeenNthCalledWith(1, "/api/v1/dossiers", request);
    expect(post).toHaveBeenNthCalledWith(2, "/api/v1/dossiers/d1/submit");
    expect(post).toHaveBeenNthCalledWith(3, "/api/v1/dossiers/d1/cancel");
  });

  it("gère le presigned upload et les documents", async () => {
    post
      .mockResolvedValueOnce({ data: { document_id: "doc1", upload_url: "https://s3", s3_key: "key" } } as never)
      .mockResolvedValueOnce({ data: { document_id: "doc1", status: "UPLOADED", uploaded_at: "now" } } as never);
    get
      .mockResolvedValueOnce({ data: [{ id: "doc1", status: "UPLOADED" }] } as never)
      .mockResolvedValueOnce({ data: { url: "https://view", expires_in: 300 } } as never);
    const payload = { document_type: "IDENTITY_CARD" as const, filename: "id.pdf", content_type: "application/pdf", size: 12 };
    expect(await DossiersClient.requestPresignedUrl("d1", payload)).toHaveProperty("document_id", "doc1");
    expect(await DossiersClient.confirmUpload("d1", "doc1")).toHaveProperty("status", "UPLOADED");
    expect(await DossiersClient.getDocuments("d1")).toHaveLength(1);
    expect(await DossiersClient.getDocumentViewUrl("d1", "doc1")).toHaveProperty("url", "https://view");
    expect(post).toHaveBeenNthCalledWith(1, "/api/v1/dossiers/d1/documents/presigned-url", payload);
    expect(post).toHaveBeenNthCalledWith(2, "/api/v1/dossiers/d1/documents/doc1/confirm");
    expect(get).toHaveBeenNthCalledWith(1, "/api/v1/dossiers/d1/documents");
    expect(get).toHaveBeenNthCalledWith(2, "/api/v1/dossiers/d1/documents/doc1/view-url");
  });

  it("récupère les dossiers client et administrateur", async () => {
    get
      .mockResolvedValueOnce({ data: [{ id: "d1" }] } as never)
      .mockResolvedValueOnce({ data: [{ id: "d2" }] } as never)
      .mockResolvedValueOnce({ data: { status: "SUBMITTED" } } as never)
      .mockResolvedValueOnce({ data: [{ id: "d3" }] } as never)
      .mockResolvedValueOnce({ data: { id: "d4" } } as never);
    expect(await DossiersClient.getMyDossiers()).toHaveLength(1);
    expect(await DossiersClient.getPendingDossiers("created_at")).toHaveLength(1);
    expect(await DossiersClient.getDossierStatus("d2")).toHaveProperty("status", "SUBMITTED");
    expect(await DossiersClient.getDossierHistory()).toHaveLength(1);
    expect(await DossiersClient.getDossierDetail("d5")).toHaveProperty("id", "d4");
    expect(get).toHaveBeenNthCalledWith(2, "/api/v1/admin/dossiers/pending", { params: { sort_by: "created_at" } });
  });

  it("exécute les actions administrateur", async () => {
    post
      .mockResolvedValueOnce({ data: { message: "ok", dossier_id: "d1", status: "VALIDATED" } } as never)
      .mockResolvedValueOnce({ data: { message: "ok", dossier_id: "d1", status: "REJECTED" } } as never)
      .mockResolvedValueOnce({ data: { message: "ok", dossier_id: "d1", status: "DOCUMENTS_PENDING" } } as never);
    await DossiersClient.validateDossier("d1", "Très bien");
    await DossiersClient.rejectDossier("d1", "Document illisible");
    await DossiersClient.requestDocuments("d1", ["PAYSLIP", "BANK_DETAILS"]);
    expect(post).toHaveBeenNthCalledWith(1, "/api/v1/admin/dossiers/d1/validate", { comment: "Très bien" });
    expect(post).toHaveBeenNthCalledWith(2, "/api/v1/admin/dossiers/d1/reject", { reason: "Document illisible" });
    expect(post).toHaveBeenNthCalledWith(3, "/api/v1/admin/dossiers/d1/request-documents", { document_types: ["PAYSLIP", "BANK_DETAILS"] });
  });
});
