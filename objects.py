import datetime
from typing import List

from pydantic import BaseModel, Field


class Object(BaseModel):
    id: int

    class Config:
        from_attributes = True


class StockIds(BaseModel):
    id: int
    remains: int


class CreateItem(BaseModel):
    article: str
    name: str = Field(min_length=5)
    description: str = Field(min_length=5)
    price: float = Field(gt=99)
    currencyCode: str | None = "RUB"
    barcode: str | None = None
    stockIds: list[StockIds]


class CreateManyItems(BaseModel):
    items: list[CreateItem]


class Remains(Object):
    stockId: int
    remains: int
    dateUpdate: datetime.datetime


class Item(Object):
    name: str
    article: str
    price: float
    remains: int | list[Remains]


class ItemFull(Item):
    currencyCode: str
    barcode: str


class ItemsList(BaseModel):
    items: list[Item]


class UDItemBody(BaseModel):
    itemId: int
    stockId: int
    remains: int


class UDBody(BaseModel):
    items: list[UDItemBody]


class CreateStock(BaseModel):
    name: str
    city: int
    capacity: int


class StockInfo(BaseModel):
    remains: int
    capacity: int
    updatedAt: datetime.datetime


class Stock(Object):
    code: str
    name: str
    city: str
    info: StockInfo


class StockFull(Stock):
    items: list[Item]


class StockList(BaseModel):
    items: list[Stock]
    total: int


class City(Object):
    name: str


class CityExtended(City):
    stocks: list[Stock] | None = None


class CitiesList(BaseModel):
    items: list[City]
    total: int


class CitiesListExtended(CitiesList):
    items: list[CityExtended]



