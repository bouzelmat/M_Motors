"""Objet‑valeur représentant le type d'énergie du véhicule."""

from enum import Enum


class EnergyType(str, Enum):
    ESSENCE = "ESSENCE"
    DIESEL = "DIESEL"
    ELECTRIQUE = "ELECTRIQUE"
    HYBRIDE = "HYBRIDE"
