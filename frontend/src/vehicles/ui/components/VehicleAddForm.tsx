import React, { useState } from "react";
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    Checkbox,
    FormControlLabel,
    FormControl,
    FormHelperText,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    Stack,
    Switch,
    TextField,
    Typography,
} from "@mui/material";

import type { CatalogType, CreateVehicleRequestDTO, EnergyType, ServiceDTO } from "../../infrastructure/dto/vehicle.dto";

interface VehicleAddFormProps {
    onSubmit: (data: CreateVehicleRequestDTO) => Promise<void>;
    isSubmitting: boolean;
    apiError: string | null;
    services: readonly ServiceDTO[];
    isLoadingServices: boolean;
    servicesError: string | null;
    initialValues?: CreateVehicleRequestDTO;
    submitLabel?: string;
}

type FormErrors = {
    brand?: string;
    model?: string;
    year?: string;
    mileage?: string;
    energy_type?: string;
    catalog_type?: string;
    price?: string;
    monthly_rent?: string;
};

export const VehicleAddForm: React.FC<VehicleAddFormProps> = ({
    onSubmit,
    isSubmitting,
    apiError,
    services,
    isLoadingServices,
    servicesError,
    initialValues,
    submitLabel = "Créer le véhicule",
}) => {
    const [brand, setBrand] = useState(initialValues?.brand ?? "");
    const [model, setModel] = useState(initialValues?.model ?? "");
    const [year, setYear] = useState<number | "">(initialValues?.year ?? new Date().getFullYear());
    const [mileage, setMileage] = useState<number | "">(initialValues?.mileage ?? 0);
    const [energyType, setEnergyType] = useState<EnergyType>(initialValues?.energy_type ?? "ESSENCE");
    const [catalogType, setCatalogType] = useState<CatalogType>(initialValues?.catalog_type ?? "RENTAL");
    const [price, setPrice] = useState<number | "">(initialValues?.price ?? "");
    const [monthlyRent, setMonthlyRent] = useState<number | "">(initialValues?.monthly_rent ?? "");
    const [description, setDescription] = useState(initialValues?.description ?? "");
    const [selectedServices, setSelectedServices] = useState<{
        service_id: string;
        included: boolean;
    }[]>(initialValues?.services.map((service) => ({ ...service })) ?? []);

    const [errors, setErrors] = useState<FormErrors>({});

    const resetForm = () => {
        setBrand("");
        setModel("");
        setYear(new Date().getFullYear());
        setMileage(0);
        setEnergyType("ESSENCE");
        setCatalogType("RENTAL");
        setPrice("");
        setMonthlyRent("");
        setDescription("");
        setSelectedServices([]);
        setErrors({});
    };

    const validate = (): boolean => {
        const newErrors: FormErrors = {};

        if (!brand.trim()) newErrors.brand = "La marque est obligatoire.";
        if (!model.trim()) newErrors.model = "Le modèle est obligatoire.";

        if (year === "" || Number(year) < 1886) {
            newErrors.year = "L'année doit être supérieure ou égale à 1886.";
        }

        if (mileage === "" || Number(mileage) < 0) {
            newErrors.mileage = "Le kilométrage doit être positif ou nul.";
        }

        if (!energyType) newErrors.energy_type = "L'énergie est obligatoire.";
        if (!catalogType) newErrors.catalog_type = "Le type de catalogue est obligatoire.";

        if ((catalogType === "SALE" || catalogType === "BOTH") && (price === "" || Number(price) <= 0)) {
            newErrors.price = "Le prix de vente est obligatoire et doit être strictement positif.";
        }

        if ((catalogType === "RENTAL" || catalogType === "BOTH") && (monthlyRent === "" || Number(monthlyRent) <= 0)) {
            newErrors.monthly_rent = "Le loyer mensuel est obligatoire et doit être strictement positif.";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        const payload: CreateVehicleRequestDTO = {
            brand: brand.trim(),
            model: model.trim(),
            year: Number(year),
            mileage: Number(mileage),
            energy_type: energyType,
            catalog_type: catalogType,
            description: description.trim() || null,
            services: catalogType === "SALE" ? [] : selectedServices,
            ...((catalogType === "SALE" || catalogType === "BOTH") ? { price: Number(price) } : {}),
            ...((catalogType === "RENTAL" || catalogType === "BOTH") ? { monthly_rent: Number(monthlyRent) } : {}),
        };

        try {
            await onSubmit(payload);
            resetForm();
        } catch {
            // L'erreur API est interceptée et gérée par le composant parent
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} noValidate>
            <Stack spacing={3}>
                {apiError && <Alert severity="error">{apiError}</Alert>}

                <TextField
                    id="vehicle-brand"
                    name="brand"
                    label="Marque"
                    value={brand}
                    onChange={(e) => setBrand(e.target.value)}
                    error={Boolean(errors.brand)}
                    helperText={errors.brand}
                    required
                    fullWidth
                />

                <TextField
                    id="vehicle-model"
                    name="model"
                    label="Modèle"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    error={Boolean(errors.model)}
                    helperText={errors.model}
                    required
                    fullWidth
                />

                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                    <TextField
                        id="vehicle-year"
                        name="year"
                        label="Année"
                        type="number"
                        value={year}
                        onChange={(e) => setYear(e.target.value === "" ? "" : Number(e.target.value))}
                        error={Boolean(errors.year)}
                        helperText={errors.year}
                        required
                        fullWidth
                    />

                    <TextField
                        id="vehicle-mileage"
                        name="mileage"
                        label="Kilométrage (km)"
                        type="number"
                        value={mileage}
                        onChange={(e) => setMileage(e.target.value === "" ? "" : Number(e.target.value))}
                        error={Boolean(errors.mileage)}
                        helperText={errors.mileage}
                        required
                        fullWidth
                    />
                </Stack>

                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                    <FormControl fullWidth required error={Boolean(errors.energy_type)}>
                        <InputLabel id="energy-type-label" htmlFor="vehicle-energy-type">Énergie</InputLabel>
                        <Select
                            id="vehicle-energy-type"
                            name="energy_type"
                            labelId="energy-type-label"
                            value={energyType}
                            label="Énergie"
                            onChange={(e) => setEnergyType(e.target.value as EnergyType)}
                        >
                            <MenuItem value="ESSENCE">Essence</MenuItem>
                            <MenuItem value="DIESEL">Diesel</MenuItem>
                            <MenuItem value="ELECTRIQUE">Électrique</MenuItem>
                            <MenuItem value="HYBRIDE">Hybride</MenuItem>
                        </Select>
                        {errors.energy_type && <FormHelperText>{errors.energy_type}</FormHelperText>}
                    </FormControl>

                    <FormControl fullWidth required error={Boolean(errors.catalog_type)}>
                        <InputLabel id="catalog-type-label" htmlFor="vehicle-catalog-type">Type de catalogue</InputLabel>
                        <Select
                            id="vehicle-catalog-type"
                            name="catalog_type"
                            labelId="catalog-type-label"
                            value={catalogType}
                            label="Type de catalogue"
                            onChange={(e) => {
                                setCatalogType(e.target.value as CatalogType);
                            }}
                        >
                            <MenuItem value="RENTAL">Location (LLD)</MenuItem>
                            <MenuItem value="SALE">Vente</MenuItem>
                            <MenuItem value="BOTH">Vente et Location</MenuItem>
                        </Select>
                        {errors.catalog_type && <FormHelperText>{errors.catalog_type}</FormHelperText>}
                    </FormControl>
                </Stack>

                {(catalogType === "SALE" || catalogType === "BOTH") && (
                    <TextField
                        id="vehicle-price"
                        name="price"
                        label="Prix de vente (€)"
                        type="number"
                        value={price}
                        onChange={(e) => setPrice(e.target.value === "" ? "" : Number(e.target.value))}
                        error={Boolean(errors.price)}
                        helperText={errors.price}
                        required
                        fullWidth
                    />
                )}

                {(catalogType === "RENTAL" || catalogType === "BOTH") && (
                    <TextField
                        id="vehicle-monthly-rent"
                        name="monthly_rent"
                        label="Loyer mensuel (€/mois)"
                        type="number"
                        value={monthlyRent}
                        onChange={(e) => setMonthlyRent(e.target.value === "" ? "" : Number(e.target.value))}
                        error={Boolean(errors.monthly_rent)}
                        helperText={errors.monthly_rent}
                        required
                        fullWidth
                    />
                )}

                {(catalogType === "RENTAL" || catalogType === "BOTH") && (
                    <Stack spacing={1.5}>
                        <Box>
                            <Typography variant="h6" fontWeight={700}>Services de location</Typography>
                        </Box>
                        {servicesError && <Alert severity="warning">{servicesError}</Alert>}
                        {isLoadingServices ? (
                            <CircularProgress size={24} aria-label="Chargement des services" />
                        ) : services.length === 0 ? (
                            <Alert severity="info">Aucun service n’est configuré dans le catalogue.</Alert>
                        ) : services.map((service) => {
                            const selection = selectedServices.find(
                                (selected) => selected.service_id === service.id,
                            );
                            const categoryLabels: Record<string, string> = {
                                INSURANCE: "Assurance",
                                ASSISTANCE: "Assistance dépannage",
                                MAINTENANCE: "Entretien et SAV",
                                INSPECTION: "Contrôle technique",
                            };
                            return (
                                <Paper key={service.id} variant="outlined" sx={{ p: 2, borderRadius: 1 }}>
                                    <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1}>
                                        <FormControlLabel
                                            control={
                                                <Checkbox
                                                    inputProps={{
                                                        id: `service-checkbox-${service.id}`,
                                                        name: `service_${service.id}`,
                                                        "aria-label": service.name,
                                                    }}
                                                    checked={Boolean(selection)}
                                                    onChange={(event) => {
                                                        setSelectedServices((current) => event.target.checked
                                                            ? [...current, { service_id: service.id, included: false }]
                                                            : current.filter((item) => item.service_id !== service.id));
                                                    }}
                                                />
                                            }
                                            label={service.name}
                                        />
                                        <Typography variant="body2" color="text.secondary" sx={{ alignSelf: "center" }}>
                                            {categoryLabels[service.category] ?? service.category} · {service.monthly_cost} €/mois
                                        </Typography>
                                    </Stack>
                                    {selection && (
                                        <FormControlLabel
                                            sx={{ ml: 4 }}
                                            control={
                                                <Switch
                                                    inputProps={{
                                                        id: `service-switch-${service.id}`,
                                                        name: `service_included_${service.id}`,
                                                    }}
                                                    checked={selection.included}
                                                    onChange={(event) => {
                                                        setSelectedServices((current) => current.map((item) =>
                                                            item.service_id === service.id
                                                                ? { ...item, included: event.target.checked }
                                                                : item,
                                                        ));
                                                    }}
                                                />
                                            }
                                            label="Inclus dans l’abonnement"
                                        />
                                    )}
                                </Paper>
                            );
                        })}
                    </Stack>
                )}

                <TextField
                    id="vehicle-description"
                    name="description"
                    label="Description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    multiline
                    rows={4}
                    fullWidth
                />

                <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={isSubmitting}
                    startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
                >
                    {isSubmitting ? "Enregistrement en cours..." : submitLabel}
                </Button>
            </Stack>
        </Box>
    );
};