from typing import List

from pydantic import BaseModel


class Object(BaseModel):
    id: int


class Stock(Object):
    name: str
    city: str
    remains: int = None
    capability: int = None
    free: float = None


class StockList(BaseModel):
    items: list[Stock]
    total: int


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
    