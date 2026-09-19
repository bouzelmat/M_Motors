"""Value object representing the type of a supporting document."""

from enum import Enum


class DocumentType(str, Enum):
    """Types of supporting documents handled in the dossier."""

    IDENTITY_CARD = "IDENTITY_CARD"
    PROOF_OF_ADDRESS = "PROOF_OF_ADDRESS"
    PAYSLIP = "PAYSLIP"
    BANK_DETAILS = "BANK_DETAILS"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    REGISTRATION_CERTIFICATE = "REGISTRATION_CERTIFICATE"
    OTHER = "OTHER"