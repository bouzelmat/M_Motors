/** Modes de consultation du catalogue. */
export type CatalogMode = "rental" | "sale";

/** DTO représentant un véhicule dans le catalogue. */
export type VehicleListItemDTO = {
    readonly id: string;
    readonly brand: string;
    readonly model: string;
    readonly year: number;
    readonly monthly_rent: string; // Decimal sérialisé en chaîne
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
    readonly price: string; // Decimal sérialisé en chaîne
    readonly mileage: number;
    readonly energy_type: string;
    readonly description: string | null;
    readonly services: readonly ServiceDTO[];
};

/** Paramètres de recherche du catalogue. */
export type GetCatalogParams = {
    readonly mode: CatalogMode;
    readonly max_monthly_rent?: number;
    readonly brand?: string;
    readonly max_price?: number;
    readonly max_mileage?: number;
    readonly fuel_type?: string;
};