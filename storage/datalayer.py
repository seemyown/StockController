import string
import random
from functools import singledispatch

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_, or_, delete, update, func as ps

from objects import City, CreateStock, CreateItem, CreateManyItems, UDBody
from storage.connection import session as factory

from storage.models import *


def session_decorator(func):
    def wrapper(*args, **kwargs):
        with factory() as session:
            return func(session, *args, **kwargs)
    return wrapper


class DataLayer:

    @staticmethod
    @session_decorator
    def get_all(session, obj):
        return session.query(obj).all()

    @staticmethod
    @session_decorator
    def get_one_by_criteria(session, obj, field, value):
        return session.query(obj).filter(getattr(obj, field) == value).first()


class CityLayer(DataLayer):

    @classmethod
    def get_cities(cls):
        return cls.get_all(Cities)

    @classmethod
    def get_city_id(cls, city_name):
        return cls.get_one_by_criteria(Cities, "name", city_name)

    @staticmethod
    @session_decorator
    def search_city(session, city_name):
        cities = session.query(Cities).where(Cities.name.ilike(f"{city_name.title()}%")).all()
        return cities

    @staticmethod
    @session_decorator
    def get_cities_extended(session):
        cities = (
            select(Cities).options(
                joinedload(Cities.stocks)
            )
        )
        cities = session.execute(cities)
        cities = cities.unique().scalars().all()
        return cities


class StockLayer(DataLayer):
    @staticmethod
    @session_decorator
    def create_stock(session, data: CreateStock):
        skl_id = random.randint(9999, 999999)
        skl_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        new_stock = Stocks(
            id=skl_id,
            code=skl_code,
            name=data.name,
            cityId=data.city,
        )
        stock_capacity = StocksCapacity(
            stockId=skl_id,
            capacity=data.capacity,
        )
        session.add_all([new_stock, stock_capacity])
        session.commit()
        return new_stock.id

    @staticmethod
    @session_decorator
    def get_stock(session, _id):
        query = select(Stocks).where(Stocks.id == _id).options(
            joinedload(Stocks.items)
        )
        stock = session.execute(query).unique().scalars().all()[0]
        return stock

    @staticmethod
    @session_decorator
    def get_stocks(session):
        query = select(Stocks)
        stocks = session.execute(query).scalars().all()
        return stocks

    @staticmethod
    @session_decorator
    def delete_stock(session, _id):
        query = (
            delete(Stocks).filter(Stocks.id == _id)
        )
        session.execute(query)
        session.commit()


class ItemLayer(DataLayer):
    @staticmethod
    @session_decorator
    def create_item(session, data: CreateItem):
        try:
            item_id = random.randint(9999, 999999)
            if data.barcode is None:
                data.barcode = "".join(random.choices(string.ascii_uppercase + string.digits, k=24))

            new_item = Items(
                id=item_id,
                article=data.article,
                barcode=data.barcode,
                name=data.name,
                description=data.description,
                price=data.price,
                currencyCode=data.currencyCode,
            )
            session.add(new_item)
            session.flush()
            stocks = []
            for stock in data.stockIds:
                stocks.append(ItemsStocks(
                    itemId=item_id,
                    stockId=stock.id,
                    remains=stock.remains
                ))
            session.add_all(stocks)
            session.commit()
            return [{
                "id": new_item.id,
                "article": data.article,
                "status": "imported",
                "err": ""
            }]
        except IntegrityError as e:
            return [{
                "id": -1,
                "article": data.article,
                "status": "declined",
                "err": str(e)
            }]

    @staticmethod
    @session_decorator
    def create_many_items(session, items: CreateManyItems):
        created_item = []
        for data in items.items:
            try:
                item_id = random.randint(9999, 999999)
                if data.barcode is None:
                    data.barcode = "".join(random.choices(string.ascii_uppercase + string.digits, k=24))

                new_item = Items(
                    id=item_id,
                    barcode=data.barcode,
                    article=data.article,
                    name=data.name,
                    description=data.description,
                    price=data.price,
                    currencyCode=data.currencyCode,
                )
                session.add(new_item)
                session.flush()
                stocks = []
                for stock in data.stockIds:
                    stocks.append(ItemsStocks(
                        itemId=item_id,
                        stockId=stock.id,
                        remains=stock.remains
                    ))
                session.add_all(stocks)
                created_item.append({
                    "id": item_id,
                    "article": data.article,
                    "status": "imported",
                    "err": ""
                })
            except IntegrityError as e:
                created_item.append({
                    "id": -1,
                    "article": data.article,
                    "status": "declined",
                    "err": str(e)
                })
        session.commit()
        return created_item

    @staticmethod
    @session_decorator
    def get_items(session):
        query = select(Items)
        items = session.execute(query).unique().scalars().all()
        return items

    @staticmethod
    @session_decorator
    def get_item(session, _id):
        query = select(Items).where(Items.id == _id)
        item = session.execute(query).unique().scalars().all()
        return item[0]

    @staticmethod
    @session_decorator
    def update_items(session, data: UDBody):
        for item in data.items:
            session.execute(
                update(ItemsStocks).filter_by(
                    itemId=item.itemId,
                    stockId=item.stockId,
                ).values(
                    remains=item.remains
                )
            )
        session.commit()

    @staticmethod
    @session_decorator
    def delete_items(session, data: UDBody):
        for item in data.items:
            session.execute(
                delete(Items).filter_by(id=item.itemId)
            )
            session.execute(
                delete(ItemsStocks).filter_by(
                    itemId=item.itemId,
                    stockId=item.stockId,
                )
            )
        session.commit()

    @staticmethod
    @session_decorator
    def stock_remains_update(session):
        stocks = session.query(ItemsStocks).all()
        stocks_list = set([stock.stockId for stock in stocks])
        stock_to_update = {}
        for stock in stocks_list:
            stock_to_update[stock] = 0
        for stock in stocks:
            stock_to_update[stock.stockId] += stock.remains

        for k, v in stock_to_update.items():
            session.execute(
                update(StocksCapacity).filter_by(stockId=k).values(remains=v)
            )
        session.commit()

