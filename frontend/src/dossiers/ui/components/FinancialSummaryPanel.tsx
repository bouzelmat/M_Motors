import React from "react";
import {
	Paper,
	Typography,
	Grid,
	Divider,
	Box,
} from "@mui/material";
import type { AdminDossierDetailResponse } from "../../../api/clients/DossiersClient";

interface FinancialSummaryPanelProps {
	dossier: AdminDossierDetailResponse;
}

export const FinancialSummaryPanel: React.FC<FinancialSummaryPanelProps> = ({
	dossier,
}) => {
	const capitalToFinance =
		dossier.vehicle_price !== null && dossier.financing_plan
			? Number(dossier.vehicle_price) - Number(dossier.financing_plan.down_payment)
			: null;

	return (
		<Paper sx={{ p: 3, mb: 3 }}>
			<Typography variant="h6" gutterBottom>
				Synthèse financière
			</Typography>

			<Grid container spacing={3}>
				{/* Section Financement */}
				<Grid item xs={12} md={6}>
					<Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
						Financement
					</Typography>
					{dossier.financing_plan ? (
						<Box>
							<Grid container spacing={1}>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Apport initial
									</Typography>
									<Typography variant="body1">
										{Number(dossier.financing_plan.down_payment).toLocaleString("fr-FR", {
											style: "currency",
											currency: "EUR",
										})}
									</Typography>
								</Grid>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Capital à financer
									</Typography>
									<Typography variant="body1">
										{capitalToFinance !== null
											? capitalToFinance.toLocaleString("fr-FR", {
													style: "currency",
													currency: "EUR",
											  })
											: "Non calculable"}
									</Typography>
								</Grid>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Durée
									</Typography>
									<Typography variant="body1">
										{dossier.financing_plan.duration_months} mois
									</Typography>
								</Grid>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Mensualité
									</Typography>
									<Typography variant="body1">
										{Number(dossier.financing_plan.monthly_payment).toLocaleString("fr-FR", {
											style: "currency",
											currency: "EUR",
										})}
									</Typography>
								</Grid>
							</Grid>
						</Box>
					) : (
						<Typography variant="body2" color="text.secondary">
							Aucun financement renseigné
						</Typography>
					)}
				</Grid>

				<Divider orientation="vertical" flexItem sx={{ display: { xs: "none", md: "block" } }} />

				{/* Section Reprise */}
				<Grid item xs={12} md={6}>
					<Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
						Reprise
					</Typography>
					{dossier.trade_in ? (
						<Box>
							<Grid container spacing={1}>
								<Grid item xs={12}>
									<Typography variant="caption" color="text.secondary">
										Immatriculation
									</Typography>
									<Typography variant="body1">
										{dossier.trade_in.registration}
									</Typography>
								</Grid>
								{(dossier.trade_in.brand || dossier.trade_in.model) && (
									<Grid item xs={12}>
										<Typography variant="caption" color="text.secondary">
											Véhicule
										</Typography>
										<Typography variant="body1">
											{[dossier.trade_in.brand, dossier.trade_in.model]
												.filter(Boolean)
												.join(" ")}
										</Typography>
									</Grid>
								)}
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Kilométrage
									</Typography>
									<Typography variant="body1">
										{dossier.trade_in.mileage.toLocaleString("fr-FR")} km
									</Typography>
								</Grid>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Estimation
									</Typography>
									<Typography variant="body1">
										{dossier.trade_in.estimated_value !== null &&
										dossier.trade_in.estimated_value !== undefined
											? Number(dossier.trade_in.estimated_value).toLocaleString("fr-FR", {
													style: "currency",
													currency: "EUR",
											  })
											: "En attente d'évaluation"}
									</Typography>
								</Grid>
							</Grid>
						</Box>
					) : (
						<Typography variant="body2" color="text.secondary">
							Aucune reprise demandée
						</Typography>
					)}
				</Grid>
			</Grid>
		</Paper>
	);
};