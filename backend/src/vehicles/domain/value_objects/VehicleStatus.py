"""Objet‑valeur énumérant les statuts possibles d'un véhicule."""

from enum import Enum


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"  # Disponible à la vente ou à la location
    RENTED = "RENTED"  # Actuellement loué
    SOLD = "SOLD"  # Vendu définitivement
    MAINTENANCE = "MAINTENANCE"  # En entretien / indisponible temporairement
