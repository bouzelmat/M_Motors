from enum import Enum

class CatalogType(str, Enum):
    RENTAL = "RENTAL"
    SALE = "SALE"