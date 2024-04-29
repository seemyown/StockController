import os.path
import random

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from objects import *
from storage.datalayer import CityLayer


class BaseAPI(APIRouter):
    def __init__(self, prefix):
        super().__init__(
            prefix=prefix
        )

    @staticmethod
    def save(data, table):
        path = f"./storage/{table}.csv"
        if os.path.exists(path):
            pd.DataFrame(data).to_csv(
                path, index=False, header=False, mode="a"
            )
        else:
            pd.DataFrame(data).to_csv(path, index=False)

    def load(self, table):
        path = f"./storage/{table}.csv"
        try:
            return pd.read_csv(path, low_memory=False)
        except FileNotFoundError as e:
            raise self.error("File does not exist", 500, e)

    @staticmethod
    def success(message, code):
        return JSONResponse(
            status_code=code,
            content={
                "statusCode": code,
                "message": message
            }
        )

    @staticmethod
    def error(message, code, error):
        raise HTTPException(
            status_code=code,
            detail={
                "statusCode": code,
                "error": error.__class__.__name__,
                "message": message
            }
        )

    def setup_routers(self):
        ...


class StocksRouters(BaseAPI):
    def __init__(self):
        super().__init__(prefix="/stocks")

    def create_new_stock(self, stock_name, stock_city, stock_capability):
        stock_id = random.randint(1, 100000)
        new_stock = Stock(
            id=stock_id,
            name=stock_name,
            city=stock_city,
            remains=0,
            capability=stock_capability,
            free=100
        ).model_dump()
        self.save([new_stock], "stocks")
        return self.success(f"StockID: {stock_id}", 201)

    def get_stock(self, stock_id: int = None):
        stock = self.load("stocks")

        if stock_id is not None:
            stock = stock.loc[stock["id"] == stock_id]

        stock_list = stock.to_dict(orient="records")
        return StockList(
            items=[Stock.model_validate(_stock) for _stock in stock_list],
            total=len(stock_list)
        )

    def search_stock(self, criteria: str = None, query: str = None):
        stock_df = self.load("stocks")

        if criteria is not None:
            stock_df = stock_df.loc[stock_df[f"{criteria}"].str.contains(query)]

        stock_list = stock_df.to_dict(orient="records")
        return StockList(
            items=[Stock.model_validate(_stock) for _stock in stock_list],
            total=len(stock_list)
        )

    def setup_routers(self):
        @self.post("/")
        def create_stock(stock: CreateStock):
            return self.create_new_stock(
                stock_name=stock.name,
                stock_city=stock.city,
                stock_capability=stock.capability
            )

        @self.get("/")
        def get_stocks(stock_id: int = None):
            return self.get_stock(stock_id)

        @self.get("/search")
        def search_stocks(query: str = None, criteria: str = None):
            return self.search_stock(criteria, query)


class CitiesRouters(BaseAPI):
    def __init__(self):
        super().__init__(
            prefix="/cities"
        )

    def setup_routers(self):
        @self.get("/", response_model_exclude=[""])
        def get_cities(stocks: bool = False):
            cities_lst = CityLayer.get_cities(stocks)
            return CitiesList(
                items=cities_lst,
                total=len(cities_lst)
            )

        @self.get("/search")
        def search_cities(query: str = None):
            cities_lst = CityLayer.search_city(query)
            return CitiesList(
                items=cities_lst,
                total=len(cities_lst)
            )





        



