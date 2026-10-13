/** Modes de consultation du catalogue. */
import type { CatalogMode } from "../../domain/value-objects/catalogMode";

export type { CatalogMode } from "../../domain/value-objects/catalogMode";
export type CatalogType = "SALE" | "RENTAL" | "BOTH";
export type EnergyType = "ESSENCE" | "DIESEL" | "ELECTRIQUE" | "HYBRIDE";

/** DTO représentant un véhicule dans le catalogue. */
export type VehicleListItemDTO = {
    readonly id: string;
    readonly brand: string;
    readonly model: string;
    readonly year: number;
    readonly monthly_rent: string | null; // Decimal sérialisé en chaîne
    readonly photo_url: string | null;
    readonly included_services: readonly string[];
};

/** DTO représentant un service optionnel. */
export type ServiceDTO = {
    readonly id: string;
    readonly name: string;
    readonly monthly_cost: string; // Decimal sérialisé en chaîne
    readonly category: string;
    readonly included: boolean;
};

/** DTO représentant le détail complet d'un véhicule. */
export type VehicleDetailDTO = VehicleListItemDTO & {
    readonly price: string | null; // Decimal sérialisé en chaîne
    readonly mileage: number;
    readonly energy_type: EnergyType;
    readonly catalog_type: CatalogType;
    readonly description: string | null;
    readonly services: readonly ServiceDTO[];
};

/** DTO de création de véhicule transmis au backend. */
export type CreateVehicleRequestDTO = {
    readonly brand: string;
    readonly model: string;
    readonly year: number;
    readonly mileage: number;
    readonly energy_type: EnergyType;
    readonly catalog_type: CatalogType;
    readonly price?: number | null;
    readonly monthly_rent?: number | null;
    readonly description?: string | null;
    readonly services: readonly {
        readonly service_id: string;
        readonly included: boolean;
    }[];
};

export type VehicleStatus = "AVAILABLE" | "RENTED" | "SOLD" | "MAINTENANCE";

/** DTO partagé par les réponses de création et de modification d'un véhicule. */
export type VehicleResponseDTO = {
    readonly id: string;
    readonly brand: string;
    readonly model: string;
    readonly year: number;
    readonly price: string | null;
    readonly monthly_rent: string | null;
    readonly mileage: number;
    readonly energy_type: EnergyType;
    readonly status: VehicleStatus;
    readonly catalog_type: CatalogType;
    readonly description: string | null;
    readonly created_at: string;
    readonly updated_at: string;
};

export type VehicleCreatedDTO = VehicleResponseDTO;

/** Paramètres de recherche du catalogue. */
export type GetCatalogParams = {
    readonly mode: CatalogMode;
    readonly max_monthly_rent?: number;
    readonly brand?: string;
    readonly max_price?: number;
    readonly max_mileage?: number;
    readonly fuel_type?: string;
};

/** Réponse de réservation d'une photo avant son upload direct vers S3. */
export type PresignedPhotoUploadDTO = {
    readonly photo_id: string;
    readonly url: string;
    readonly fields: Readonly<Record<string, string>>;
};

/** Réponse de confirmation d'une photo effectivement déposée dans S3. */
export type ConfirmPhotoUploadDTO = {
    readonly photo_id: string;
    readonly photo_url: string;
};

export type VehiclePhotoDTO = {
    readonly id: string;
    readonly photo_url: string;
    readonly is_primary: boolean;
    readonly created_at: string;
    readonly uploaded_at: string | null;
};