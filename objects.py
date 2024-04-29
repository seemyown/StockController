import datetime
from typing import List

from pydantic import BaseModel


class Object(BaseModel):
    id: int

    class Config:
        from_attributes = True


class Item(Object):
    name: str
    description: str
    price: float
    remains: int = None
    stocks: list[int] = None


class ItemsList(BaseModel):
    items: list[Item]


class CreateStock(BaseModel):
    name: str
    city: str
    capability: int


class StockInfo(BaseModel):
    remains: int
    capacity: int
    freeSpace: float
    updatedAt: datetime.datetime


class Stock(Object):
    code: str
    name: str
    info: StockInfo


class City(Object):
    name: str
    stocks: list[Stock] = None


class CitiesList(BaseModel):
    items: list[City]
    total: int
