import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import axios from "axios";
import { DocumentUploader } from "../DocumentUploader";
import { DossiersClient } from "../../../../api/clients/DossiersClient";

// Mock d'Axios incluant la structure nécessaire pour apiClient.ts
vi.mock("axios", () => {
    const mockAxiosInstance = {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        interceptors: {
            request: { use: vi.fn(), eject: vi.fn() },
            response: { use: vi.fn(), eject: vi.fn() },
        },
    };

    return {
        default: {
            create: vi.fn(() => mockAxiosInstance),
            put: vi.fn(),
            isAxiosError: vi.fn((error: unknown) => Boolean((error as { isAxiosError?: boolean })?.isAxiosError)),
        },
    };
});

vi.mock("../../../../api/clients/DossiersClient");

describe("DocumentUploader", () => {
    const dossierId = "dossier-123";
    const onUploadComplete = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    test("rejette un fichier supérieur à 10 Mo", async () => {
        const user = userEvent.setup();

        render(
            <DocumentUploader dossierId={dossierId} onUploadComplete={onUploadComplete} />
        );

        const largeFile = new File(["a".repeat(11 * 1024 * 1024)], "heavy.pdf", {
            type: "application/pdf",
        });

        // Récupération de l'input type="file" via son aria-label ou selector hidden
        const input = screen.getByLabelText(/file upload/i, { selector: "input" });

        await user.upload(input, largeFile);

        await waitFor(() => {
            expect(
                screen.getByText(/Le fichier dépasse la limite autorisée de 10 Mo/i)
            ).toBeInTheDocument();
        });
    });

    test("exécute les 3 étapes d'upload dans l'ordre chronologique", async () => {
        const user = userEvent.setup();

        const mockPresigned = {
            document_id: "doc-999",
            upload_url: "https://s3/presigned-url",
            s3_key: "keys/doc-999.pdf",
        };

        vi.mocked(DossiersClient.requestPresignedUrl).mockResolvedValueOnce(mockPresigned);
        vi.mocked(axios.put).mockResolvedValueOnce({ status: 200 });
        vi.mocked(DossiersClient.confirmUpload).mockResolvedValueOnce({
            document_id: "doc-999",
            status: "UPLOADED",
            uploaded_at: new Date().toISOString(),
        });

        render(
            <DocumentUploader dossierId={dossierId} onUploadComplete={onUploadComplete} />
        );

        const validFile = new File(["valid-content"], "cni.pdf", {
            type: "application/pdf",
        });

        const input = screen.getByLabelText(/file upload/i, { selector: "input" });

        await user.upload(input, validFile);

        await waitFor(() => {
            expect(DossiersClient.requestPresignedUrl).toHaveBeenCalledWith(
                dossierId,
                expect.objectContaining({ filename: "cni.pdf" })
            );
            expect(axios.put).toHaveBeenCalledWith("https://s3/presigned-url", validFile, expect.anything());
            expect(DossiersClient.confirmUpload).toHaveBeenCalledWith(dossierId, "doc-999");
            expect(onUploadComplete).toHaveBeenCalled();
        });
    });

    test("conserve le type de document imposé par une demande complémentaire", async () => {
        const user = userEvent.setup();
        vi.mocked(DossiersClient.requestPresignedUrl).mockResolvedValueOnce({
            document_id: "doc-pay-1",
            upload_url: "https://s3/presigned-url",
            s3_key: "keys/doc-pay-1.pdf",
        });
        vi.mocked(axios.put).mockResolvedValueOnce({ status: 200 });
        vi.mocked(DossiersClient.confirmUpload).mockResolvedValueOnce({
            document_id: "doc-pay-1",
            status: "UPLOADED",
            uploaded_at: new Date().toISOString(),
        });

        render(
            <DocumentUploader
                dossierId={dossierId}
                fixedDocumentType="PAYSLIP"
                onUploadComplete={onUploadComplete}
            />
        );

        expect(screen.getByText("Type demandé : Fiche de paie")).toBeInTheDocument();
        await user.upload(
            screen.getByLabelText(/file upload/i, { selector: "input" }),
            new File(["payslip"], "bulletin.pdf", { type: "application/pdf" }),
        );

        await waitFor(() => {
            expect(DossiersClient.requestPresignedUrl).toHaveBeenCalledWith(
                dossierId,
                expect.objectContaining({ document_type: "PAYSLIP" }),
            );
        });
    });

    test("affiche un message clair lors d'une panne serveur", async () => {
        const user = userEvent.setup();
        vi.mocked(DossiersClient.requestPresignedUrl).mockRejectedValueOnce({
            isAxiosError: true,
            response: { status: 503, data: {} },
        });

        render(
            <DocumentUploader dossierId={dossierId} onUploadComplete={onUploadComplete} />
        );

        const input = screen.getByLabelText(/file upload/i, { selector: "input" });
        await user.upload(input, new File(["content"], "identity.pdf", { type: "application/pdf" }));

        expect(await screen.findByText(/problème technique/)).toBeInTheDocument();
    });
});