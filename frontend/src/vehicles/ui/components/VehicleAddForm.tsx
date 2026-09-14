import React, { useState } from "react";
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    FormControl,
    FormHelperText,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    TextField,
} from "@mui/material";

import { CreateVehicleRequestDTO } from "../../infrastructure/vehicle.types";

interface VehicleAddFormProps {
    onSubmit: (data: CreateVehicleRequestDTO) => Promise<void>;
    isSubmitting: boolean;
    apiError: string | null;
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
}) => {
    const [brand, setBrand] = useState("");
    const [model, setModel] = useState("");
    const [year, setYear] = useState<number | "">(new Date().getFullYear());
    const [mileage, setMileage] = useState<number | "">(0);
    const [energyType, setEnergyType] = useState("GASOLINE");
    const [catalogType, setCatalogType] = useState<"SALE" | "RENTAL" | "BOTH">("RENTAL");
    const [price, setPrice] = useState<number | "">("");
    const [monthlyRent, setMonthlyRent] = useState<number | "">("");
    const [description, setDescription] = useState("");

    const [errors, setErrors] = useState<FormErrors>({});

    const resetForm = () => {
        setBrand("");
        setModel("");
        setYear(new Date().getFullYear());
        setMileage(0);
        setEnergyType("GASOLINE");
        setCatalogType("RENTAL");
        setPrice("");
        setMonthlyRent("");
        setDescription("");
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
        };

        if (catalogType === "SALE" || catalogType === "BOTH") {
            payload.price = Number(price);
        }
        if (catalogType === "RENTAL" || catalogType === "BOTH") {
            payload.monthly_rent = Number(monthlyRent);
        }

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
                    label="Marque"
                    value={brand}
                    onChange={(e) => setBrand(e.target.value)}
                    error={Boolean(errors.brand)}
                    helperText={errors.brand}
                    required
                    fullWidth
                />

                <TextField
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
                        <InputLabel id="energy-type-label">Énergie</InputLabel>
                        <Select
                            labelId="energy-type-label"
                            value={energyType}
                            label="Énergie"
                            onChange={(e) => setEnergyType(e.target.value)}
                        >
                            <MenuItem value="GASOLINE">Essence</MenuItem>
                            <MenuItem value="DIESEL">Diesel</MenuItem>
                            <MenuItem value="ELECTRIC">Électrique</MenuItem>
                            <MenuItem value="HYBRID">Hybride</MenuItem>
                        </Select>
                        {errors.energy_type && <FormHelperText>{errors.energy_type}</FormHelperText>}
                    </FormControl>

                    <FormControl fullWidth required error={Boolean(errors.catalog_type)}>
                        <InputLabel id="catalog-type-label">Type de catalogue</InputLabel>
                        <Select
                            labelId="catalog-type-label"
                            value={catalogType}
                            label="Type de catalogue"
                            onChange={(e) => {
                                setCatalogType(e.target.value as "SALE" | "RENTAL" | "BOTH");
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

                <TextField
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
                    {isSubmitting ? "Création en cours..." : "Créer le véhicule"}
                </Button>
            </Stack>
        </Box>
    );
};