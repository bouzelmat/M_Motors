import React from "react";
import type { DossierStatus } from "../../../api/clients/DossiersClient";

interface DossierStatusCardProps {
	readonly status: DossierStatus;
	readonly updatedAt: string;
	readonly decisionComment?: string | null;
}

interface StatusVisualConfig {
	readonly label: string;
	readonly description: string;
	readonly badgeClasses: string;
}

const STATUS_VISUALS: Record<DossierStatus, StatusVisualConfig> = {
	DRAFT: {
		label: "Brouillon / En préparation",
		description: "Votre dossier est en cours de création. Vous pouvez modifier vos informations et charger vos documents.",
		badgeClasses: "bg-gray-100 text-gray-800 border-gray-300",
	},
	SUBMITTED: {
		label: "Dossier soumis",
		description: "Votre dossier a été transmis avec succès. Il est actuellement en cours d'instruction.",
		badgeClasses: "bg-blue-100 text-blue-800 border-blue-300",
	},
	VALIDATED: {
		label: "Dossier validé",
		description: "Félicitations, votre dossier a été analysé et accepté.",
		badgeClasses: "bg-green-100 text-green-800 border-green-300",
	},
	REJECTED: {
		label: "Dossier refusé",
		description: "Votre dossier n'a pas pu être accepté lors de l'instruction.",
		badgeClasses: "bg-red-100 text-red-800 border-red-300",
	},
	EXPIRED: {
		label: "Dossier expiré",
		description: "Le délai imparti pour finaliser ou traiter ce dossier est dépassé.",
		badgeClasses: "bg-amber-100 text-amber-800 border-amber-300",
	},
	CANCELLED: {
		label: "Demande annulée",
		description: "Cette demande a été annulée par le client.",
		badgeClasses: "bg-gray-100 text-gray-600 border-gray-200",
	},
	DOCUMENTS_PENDING: {
		label: "Pièces complémentaires demandées",
		description: "Des documents complémentaires sont nécessaires pour poursuivre l’instruction.",
		badgeClasses: "bg-amber-100 text-amber-800 border-amber-300",
	},
};

export const DossierStatusCard: React.FC<DossierStatusCardProps> = ({
	status,
	updatedAt,
	decisionComment,
}) => {
	const visual = STATUS_VISUALS[status] ?? {
		label: status,
		description: "Statut non reconnu.",
		badgeClasses: "bg-gray-100 text-gray-600 border-gray-200",
	};

	const formattedDate = new Date(updatedAt).toLocaleDateString("fr-FR", {
		day: "2-digit",
		month: "long",
		year: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	});

	return (
		<div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
			<div className="flex items-center justify-between gap-4">
				<span
					className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${visual.badgeClasses}`}
				>
					{visual.label}
				</span>
				<span className="text-xs text-gray-500">
					Dernière mise à jour : {formattedDate}
				</span>
			</div>

			<p className="mt-4 text-sm text-gray-700">{visual.description}</p>

			{status === "REJECTED" && decisionComment && (
				<div className="mt-4 rounded-md border border-red-200 bg-red-50 p-4">
					<p className="text-xs font-semibold text-red-800">
						Motif du refus :
					</p>
					<p className="mt-1 text-sm text-red-700">{decisionComment}</p>
				</div>
			)}
		</div>
	);
};