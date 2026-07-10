import {
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	Container,
	Stack,
	Typography,
} from "@mui/material"

const highlights = [
	{
		label: "CI/CD",
		value: "GitHub Actions",
		description: "Lint, tests et déploiement automatisé sur chaque merge validé.",
	},
	{
		label: "Backend",
		value: "FastAPI + SQLAlchemy",
		description: "Une base API prête pour le PostgreSQL du docker-compose.",
	},
	{
		label: "Production",
		value: "Render puis AWS",
		description: "Un chemin MVP simple, puis une trajectoire ECS/Fargate.",
	},
]

export default function App() {
	return (
		<Box
			sx={{
				minHeight: "100vh",
				background:
					"radial-gradient(circle at top, rgba(245,158,11,0.18), transparent 32%), linear-gradient(180deg, #f4efe8 0%, #ffffff 100%)",
				py: { xs: 4, md: 8 },
			}}
		>
			<Container maxWidth="lg">
				<Stack spacing={6}>
					<Stack spacing={2} maxWidth={760}>
						<Chip label="M-Motors · CI/CD prêt" color="secondary" />
						<Typography variant="h2" component="h1" fontWeight={800}>
							Déploiement automatisé, validation continue, base technique alignée.
						</Typography>
						<Typography variant="h6" color="text.secondary">
							Le socle Frontend est prêt pour les builds Vite, les tests Vitest et
							les futurs parcours métier autour de la location longue durée.
						</Typography>
						<Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
							<Button variant="contained" size="large">
								Ouvrir le pipeline
							</Button>
							<Button variant="outlined" size="large">
								Vérifier la santé
							</Button>
						</Stack>
					</Stack>

					<Stack direction={{ xs: "column", md: "row" }} spacing={3}>
						{highlights.map((highlight) => (
							<Box key={highlight.label} sx={{ flex: 1 }}>
								<Card
									elevation={0}
									sx={{
										height: "100%",
										border: "1px solid rgba(22,50,79,0.12)",
										backgroundColor: "rgba(255,255,255,0.8)",
										backdropFilter: "blur(10px)",
									}}
								>
									<CardContent>
										<Stack spacing={1.5}>
											<Typography variant="overline" color="text.secondary">
												{highlight.label}
											</Typography>
											<Typography variant="h5" component="h2" fontWeight={700}>
												{highlight.value}
											</Typography>
											<Typography color="text.secondary">
												{highlight.description}
											</Typography>
										</Stack>
									</CardContent>
								</Card>
								</Box>
						))}
						</Stack>
				</Stack>
			</Container>
		</Box>
	)
}
