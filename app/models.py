from pydantic import BaseModel
import time
from datetime import date
from typing import List

class Item(BaseModel):
    shortDescription: str
    price: float

class Receipt(BaseModel):
    retailer: str
    purchaseDate: date
    purchaseTime: str 
    items: List[Item]
    total: float


