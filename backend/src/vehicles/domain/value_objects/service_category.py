from enum import Enum


class ServiceCategory(str, Enum):
    INSURANCE = "INSURANCE"
    ASSISTANCE = "ASSISTANCE"
    MAINTENANCE = "MAINTENANCE"
    INSPECTION = "INSPECTION"
