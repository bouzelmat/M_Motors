import { useEffect, useState } from "react";
import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Container,
	Grid,
	Paper,
	Slider,
	Stack,
	TextField,
	Typography,
} from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useNavigate, useSearchParams } from "react-router-dom";

import { calculateMonthlyPayment } from "../../../dossiers/application/utils/financing";
import { useSubscriptionTunnelStore } from "../../application/stores/useSubscriptionTunnelStore";
import { useVehicleDetailQuery } from "../../application/hooks/useVehicleDetailQuery";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";

const DEFAULT_AMOUNT = 25000;
const DEFAULT_DURATION = 48;
const INDICATIVE_RATE = 0.045;

export const SimulatorPage = () => {
	const [searchParams] = useSearchParams();
	const navigate = useNavigate();
	const vehicleId = searchParams.get("vehicleId");
	const { data: vehicle, isLoading, error } = useVehicleDetailQuery(vehicleId ?? "");
	const setVehicle = useSubscriptionTunnelStore((state) => state.setVehicle);
	const setFinancingPlan = useSubscriptionTunnelStore((state) => state.setFinancingPlan);
	const savedFinancingPlan = useSubscriptionTunnelStore((state) => state.financingPlan);
	const [amount, setAmount] = useState(DEFAULT_AMOUNT);
	const [durationMonths, setDurationMonths] = useState(savedFinancingPlan?.duration_months ?? DEFAULT_DURATION);

	useEffect(() => {
		if (!vehicle) return;
		const price = Number(vehicle.price);
		const monthlyRent = Number(vehicle.monthly_rent);
		const prefilledAmount = price > 0
			? price
			: monthlyRent > 0
				? monthlyRent * DEFAULT_DURATION
				: DEFAULT_AMOUNT;
		setAmount(prefilledAmount);
		setVehicle(vehicle.id, "rental");
	}, [vehicle, setVehicle]);

	const monthlyPayment = calculateMonthlyPayment(
		Math.max(0, amount),
		0,
		durationMonths,
		INDICATIVE_RATE,
	);

	const handleValidate = () => {
		setFinancingPlan({
			down_payment: 0,
			duration_months: durationMonths,
			monthly_payment: monthlyPayment,
		});
		if (!vehicleId || !vehicle) {
			navigate("/catalogue?mode=rental");
			return;
		}
		setVehicle(vehicle.id, "rental");
		const simulationId = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
		navigate(`/dossiers/new?simulationId=${encodeURIComponent(simulationId)}&vehicleId=${encodeURIComponent(vehicle.id)}&mode=rental`);
	};

	if (vehicleId && isLoading) {
		return <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}><CircularProgress aria-label="Chargement du véhicule" /></Box>;
	}

	if (vehicleId && (error || !vehicle)) {
		return <Container maxWidth="md" sx={{ py: 5 }}><Alert severity="error">{getApiErrorMessage(error, "Impossible de charger ce véhicule pour la simulation.")}</Alert></Container>;
	}

	const displayAmount = amount.toLocaleString("fr-FR", { maximumFractionDigits: 0 });

	return (
		<Container maxWidth="lg" sx={{ py: { xs: 4, md: 7 } }}>
			<Typography variant="overline" color="primary.main" fontWeight={800}>SIMULATION LLD</Typography>
			<Typography variant="h3" component="h1" fontWeight={800} sx={{ mb: 1 }}>Votre estimation, votre rythme.</Typography>
			<Typography color="text.secondary" sx={{ mb: 4 }}>
				{vehicle ? `Estimation prévisionnelle pour ${vehicle.brand} ${vehicle.model} (${vehicle.year}).` : "Ajustez le montant et la durée pour estimer votre mensualité."}
			</Typography>

			<Grid container spacing={4}>
				<Grid item xs={12} md={7}>
					<Paper variant="outlined" sx={{ p: { xs: 2.5, md: 4 }, borderRadius: 1 }}>
						<Stack spacing={4}>
							{vehicle && (
								<Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }}>
									<Box component="img" src={vehicle.photo_url ?? "/placeholder-car.png"} alt={`${vehicle.brand} ${vehicle.model}`} sx={{ width: { xs: "100%", sm: 180 }, aspectRatio: "16 / 10", objectFit: "cover", bgcolor: "grey.100" }} />
									<Box>
										<Typography variant="h6" fontWeight={750}>{vehicle.brand} {vehicle.model}</Typography>
										<Typography color="text.secondary">{vehicle.year} · {vehicle.energy_type}</Typography>
									</Box>
								</Stack>
							)}
							<TextField
								label="Montant de référence (€)"
								type="number"
								value={amount}
								onChange={(event) => setAmount(Math.max(0, Number(event.target.value)))}
								inputProps={{ min: 0, step: 500 }}
							/>
							<Box>
								<Typography id="simulator-duration-label" variant="subtitle1" fontWeight={700}>
									Durée : {durationMonths} mois
								</Typography>
								<Slider
									aria-labelledby="simulator-duration-label"
									min={12}
									max={60}
									step={12}
									value={durationMonths}
									onChange={(_event, value) => setDurationMonths(Array.isArray(value) ? value[0] : value)}
								/>
								<Stack direction="row" justifyContent="space-between" color="text.secondary">
									<Typography variant="caption">12 mois</Typography><Typography variant="caption">60 mois</Typography>
								</Stack>
							</Box>
						</Stack>
					</Paper>
				</Grid>
				<Grid item xs={12} md={5}>
					<Paper elevation={0} sx={{ p: 3, bgcolor: "#eef1f2", borderRadius: 1 }}>
						<Typography variant="body2" color="text.secondary">Montant de référence : {displayAmount} €</Typography>
						<Typography variant="h3" fontWeight={800} color="primary.main" sx={{ my: 1 }}>
							{monthlyPayment.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €
						</Typography>
						<Typography color="text.secondary" sx={{ mb: 3 }}>par mois · estimation indicative hors options et sous réserve d’étude du dossier.</Typography>
						<Button fullWidth variant="contained" size="large" endIcon={<ArrowForwardIcon />} onClick={handleValidate}>
							{vehicleId ? "Valider la simulation" : "Choisir un véhicule"}
						</Button>
					</Paper>
				</Grid>
			</Grid>
		</Container>
	);
};