from enum import Enum

class BusinessType(str, Enum):
    RESTAURANT = "RESTAURANT"
    HOTEL = "HOTEL"
    RETAIL = "RETAIL"
    ENTERTAINMENT = "ENTERTAINMENT"
    WELLNESS = "WELLNESS"
    
    def __str__(self):
        return self.value
