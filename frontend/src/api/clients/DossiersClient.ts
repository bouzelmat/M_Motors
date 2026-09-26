import { apiClient } from "../apiClient";

export type DocumentType =
    | "IDENTITY_CARD"
    | "PROOF_OF_ADDRESS"
    | "PAYSLIP"
    | "BANK_DETAILS"
    | "DRIVERS_LICENSE"
    | "REGISTRATION_CERTIFICATE"
    | "OTHER";

export type DocumentStatus = "PENDING" | "UPLOADED" | "REJECTED" | "VALIDATED";

export type DossierStatus =
    | "DRAFT"
    | "SUBMITTED"
    | "VALIDATED"
    | "REJECTED"
    | "EXPIRED"
    | "DOCUMENTS_PENDING";

export type TradeInRequest = {
    readonly registration: string;
    readonly mileage: number;
    readonly brand?: string | null;
    readonly model?: string | null;
};

export type FinancingPlanRequest = {
    readonly down_payment: number;
    readonly duration_months: number;
    readonly monthly_payment: number;
};

export type CreateDossierRequest = {
    readonly vehicle_id: string;
    readonly trade_in: TradeInRequest | null;
    readonly financing_plan: FinancingPlanRequest | null;
};

export type DossierResponse = {
    readonly id: string;
    readonly vehicle_id: string;
    readonly status: DossierStatus;
};

export type PresignedUrlRequest = {
    readonly document_type: DocumentType;
    readonly filename: string;
    readonly content_type: string;
    readonly size: number;
};

export type PresignedUrlResponse = {
    readonly document_id: string;
    readonly upload_url: string;
    readonly s3_key: string;
};

export type DocumentConfirmResponse = {
    readonly document_id: string;
    readonly status: DocumentStatus;
    readonly uploaded_at: string;
};

export type DocumentListItem = {
    readonly id: string;
    readonly type: DocumentType;
    readonly status: DocumentStatus;
    readonly original_filename: string;
    readonly content_type: string;
    readonly size: number;
    readonly created_at: string;
    readonly uploaded_at?: string | null;
};

export type DossierListItem = {
    readonly id: string;
    readonly vehicle_id: string;
    readonly status: DossierStatus;
    readonly created_at: string;
    readonly updated_at: string;
};

export type DossierStatusResponse = {
    readonly status: DossierStatus;
    readonly updated_at: string;
    readonly decision_comment?: string | null;
};

export type PendingDossierItem = {
    readonly id: string;
    readonly client_email: string;
    readonly vehicle_brand: string;
    readonly vehicle_model: string;
    readonly status: DossierStatus;
    readonly submitted_at: string;
    readonly created_at: string;
};

export type FinancingPlan = {
    readonly down_payment: number;
    readonly duration_months: number;
    readonly monthly_payment: number;
};

export type TradeIn = {
    readonly registration: string;
    readonly mileage: number;
    readonly brand?: string | null;
    readonly model?: string | null;
    readonly estimated_value?: number | null;
};

export type AdminDossierDetailResponse = {
    readonly id: string;
    readonly user_id: string;
    readonly client_email: string;
    readonly vehicle_id: string;
    readonly vehicle_brand: string;
    readonly vehicle_model: string;
    readonly vehicle_price?: number | null;
    readonly status: DossierStatus;
    readonly submitted_at: string | null;
    readonly created_at: string;
    readonly updated_at: string;
    readonly financing_plan: FinancingPlan | null;
    readonly trade_in: TradeIn | null;
    readonly documents: DocumentListItem[];
    readonly comment?: string | null;
    readonly rejection_reason?: string | null;
    readonly requested_document_types?: DocumentType[] | null;
};

export const DossiersClient = {
    async createDossier(data: CreateDossierRequest): Promise<DossierResponse> {
        const response = await apiClient.post<DossierResponse>("/api/v1/dossiers", data);
        return response.data;
    },

    async requestPresignedUrl(dossierId: string, data: PresignedUrlRequest): Promise<PresignedUrlResponse> {
        const response = await apiClient.post<PresignedUrlResponse>(
            `/api/v1/dossiers/${dossierId}/documents/presigned-url`,
            data
        );
        return response.data;
    },

    async confirmUpload(dossierId: string, documentId: string): Promise<DocumentConfirmResponse> {
        const response = await apiClient.post<DocumentConfirmResponse>(
            `/api/v1/dossiers/${dossierId}/documents/${documentId}/confirm`
        );
        return response.data;
    },

    async getDocuments(dossierId: string): Promise<DocumentListItem[]> {
        const response = await apiClient.get<DocumentListItem[]>(`/api/v1/dossiers/${dossierId}/documents`);
        return response.data;
    },

    async getMyDossiers(): Promise<DossierListItem[]> {
        const response = await apiClient.get<DossierListItem[]>("/api/v1/dossiers/me");
        return response.data;
    },

    async getDossierStatus(dossierId: string): Promise<DossierStatusResponse> {
        const response = await apiClient.get<DossierStatusResponse>(`/api/v1/dossiers/${dossierId}/status`);
        return response.data;
    },

    async getPendingDossiers(sortBy: string = "submitted_at"): Promise<PendingDossierItem[]> {
        const response = await apiClient.get<PendingDossierItem[]>("/api/v1/admin/dossiers/pending", {
            params: { sort_by: sortBy },
        });
        return response.data;
    },

    async getDossierDetail(dossierId: string): Promise<AdminDossierDetailResponse> {
        const response = await apiClient.get<AdminDossierDetailResponse>(`/api/v1/admin/dossiers/${dossierId}`);
        return response.data;
    },

    async validateDossier(dossierId: string, comment?: string): Promise<{ message: string; dossier_id: string; status: DossierStatus }> {
        const response = await apiClient.post(`/api/v1/admin/dossiers/${dossierId}/validate`, { comment });
        return response.data;
    },

    async rejectDossier(dossierId: string, reason: string): Promise<{ message: string; dossier_id: string; status: DossierStatus }> {
        const response = await apiClient.post(`/api/v1/admin/dossiers/${dossierId}/reject`, { reason });
        return response.data;
    },

    async requestDocuments(dossierId: string, documentTypes: DocumentType[]): Promise<{ message: string; dossier_id: string; status: DossierStatus }> {
        const response = await apiClient.post(`/api/v1/admin/dossiers/${dossierId}/request-documents`, {
            document_types: documentTypes,
        });
        return response.data;
    },
};