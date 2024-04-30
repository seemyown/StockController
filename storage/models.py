import datetime
from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, TIMESTAMP, Integer

from storage.connection import engine


IntPK = Annotated[
    int,
    mapped_column(Integer, primary_key=True, autoincrement=True)
]
DateUpdate = Annotated[
    datetime.datetime,
    mapped_column(
        TIMESTAMP, default=datetime.datetime.now,
        onupdate=datetime.datetime.now
    )
]


class Base(DeclarativeBase):
    pass


class Cities(Base):
    __tablename__ = 'cities'

    id: Mapped[IntPK]
    name: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]

    stocks: Mapped[list["Stocks"]] = relationship(
        back_populates="_city"
    )


class Stocks(Base):
    __tablename__ = 'stocks'

    id: Mapped[IntPK]
    code: Mapped[str]
    name: Mapped[str]
    cityId: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE")
    )

    _city: Mapped["Cities"] = relationship(
        back_populates="stocks",
        lazy="joined",
    )

    @property
    def city(self):
        return self._city.name

    _capacity: Mapped["StocksCapacity"] = relationship(
        back_populates="stock",
        order_by="StocksCapacity.dateUpdate.desc()",
        lazy="joined"
    )

    @property
    def info(self):
        return {
            "remains": self._capacity.remains,
            "capacity": self._capacity.capacity,
            "freeSpace": self._capacity.freePercent,
            "updatedAt": self._capacity.dateUpdate
        }

    items: Mapped[list["ItemsStocks"]] = relationship(
        back_populates="stocks",
    )


class StocksCapacity(Base):
    __tablename__ = 'stocks_capability'

    id: Mapped[IntPK]
    stockId: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE")
    )
    remains: Mapped[int] = mapped_column(default=0)
    capacity: Mapped[int]
    freePercent: Mapped[float] = mapped_column(default=100.0)
    dateUpdate: Mapped[DateUpdate]

    stock: Mapped["Stocks"] = relationship(
        back_populates="_capacity",
        lazy="joined"
    )


class Items(Base):
    __tablename__ = "items"

    id: Mapped[IntPK]
    article: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    currencyCode: Mapped[str] = mapped_column(default="RUB")
    barcode: Mapped[int]

    remains: Mapped[list["ItemsStocks"]] = relationship(
        back_populates="item",
        lazy="joined"
    )


class ItemsStocks(Base):
    __tablename__ = 'items_stocks'

    id: Mapped[IntPK]
    itemId: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    stockId: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    remains: Mapped[int] = mapped_column(default=0)
    dateUpdate: Mapped[DateUpdate]

    item: Mapped["Items"] = relationship(
        back_populates="remains",
        lazy="joined"
    )

    @property
    def name(self):
        return self.item.name

    @property
    def article(self):
        return self.item.article

    @property
    def description(self):
        return self.item.description

    @property
    def price(self):
        return self.item.price

    stocks: Mapped[list["Stocks"]] = relationship(
        back_populates="items",
        lazy="joined"
    )


def create_all_tables():
    Base.metadata.create_all(bind=engine)
