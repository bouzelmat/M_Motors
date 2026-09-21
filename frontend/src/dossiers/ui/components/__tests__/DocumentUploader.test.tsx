import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import axios from "axios";
import { DocumentUploader } from "../DocumentUploader";
import { DossiersClient } from "../../../../api/clients/DossiersClient";

vi.mock("axios");
vi.mock("../../../api/clients/DossiersClient");

describe("DocumentUploader", () => {
	const dossierId = "dossier-123";
	const onUploadComplete = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("rejette un fichier supérieur à 10 Mo", async () => {
		render(
			<DocumentUploader dossierId={dossierId} onUploadComplete={onUploadComplete} />
		);

		const largeFile = new File(["a".repeat(11 * 1024 * 1024)], "heavy.pdf", {
			type: "application/pdf",
		});

		const input = screen.getByRole("textbox", { hidden: true });
		Object.defineProperty(input, "files", { value: [largeFile] });
		fireEvent.change(input);

		await waitFor(() => {
			expect(
				screen.getByText(/Le fichier dépasse la limite autorisée de 10 Mo/i)
			).toBeInTheDocument();
		});
	});

	test("exécute les 3 étapes d'upload dans l'ordre chronologique", async () => {
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

		const input = screen.getByRole("textbox", { hidden: true });
		Object.defineProperty(input, "files", { value: [validFile] });
		fireEvent.change(input);

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
});