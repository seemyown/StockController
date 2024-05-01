from fastapi import APIRouter, HTTPException

from objects import *
from storage.datalayer import CityLayer, StockLayer, ItemLayer


class BaseAPI(APIRouter):
    def __init__(self, prefix):
        super().__init__(
            prefix=prefix
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

    def setup_routers(self):
        @self.post("/")
        def create_stock(body: CreateStock):
            try:
                new_stock = StockLayer.create_stock(body)
                return {
                    "statusCode": 200,
                    "message": "Stock created",
                    "data": new_stock
                }
            except Exception as e:
                self.error(str(e), 400, e)

        @self.get("/", response_model=StockList)
        def get_stocks():
            stocks_lst = StockLayer.get_stocks()
            return StockList(
                items=stocks_lst,
                total=len(stocks_lst)
            )

        @self.get("/{_id}", response_model=StockFull)
        def get_stock_by_id(_id: int):
            stock = StockLayer.get_stock(_id)
            return StockFull.model_validate(stock, from_attributes=True)

        @self.delete("/{_id}")
        def delete_stock_by_id(_id: int):
            StockLayer.delete_stock(_id)
            return {
                "statusCode": 202,
                "message": "Stock deleted"
            }


class CitiesRouters(BaseAPI):
    def __init__(self):
        super().__init__(
            prefix="/cities"
        )

    def setup_routers(self):
        @self.get("/", response_model=CitiesList | CitiesListExtended)
        def get_cities(extend: bool = False):
            if not extend:
                cities_lst = CityLayer.get_cities()
                return CitiesList(
                    items=cities_lst,
                    total=len(cities_lst)
                )
            else:
                cities_lst = CityLayer.get_cities_extended()
                return CitiesListExtended(
                    items=cities_lst,
                    total=len(cities_lst)
                )

        @self.get("/search", response_model=CitiesList)
        def search_cities(query: str):
            cities_lst = CityLayer.search_city(query)
            return CitiesList(
                items=cities_lst,
                total=len(cities_lst)
            ).model_dump(exclude_none=True)


class ItemsRouters(BaseAPI):
    def __init__(self):
        super().__init__(
            prefix="/items"
        )

    def setup_routers(self):
        @self.post("/", status_code=201)
        def create_item(body: CreateManyItems):
            result = ItemLayer.create_many_items(body)
            return {
                "statusCode": 201,
                "data": result
            }

        @self.get("/", response_model=ItemsList)
        def get_items():
            items_lst = ItemLayer.get_items()
            return ItemsList(
                items=items_lst,
                total=len(items_lst)
            )

        @self.get("/{_id}", response_model=ItemFull)
        def get_item_by_id(_id: int):
            item = ItemLayer.get_item(_id)
            return ItemFull.model_validate(item, from_attributes=True)

        @self.delete("/", status_code=204)
        def delete_items(data: UDBody):
            try:
                ItemLayer.delete_items(data)

            except Exception as e:
                self.error(str(e), 404, e)
            finally:
                ItemLayer.stock_remains_update()

        @self.patch("/", status_code=204)
        def update_items(data: UDBody):
            try:
                ItemLayer.update_items(data)
            except Exception as e:
                self.error(str(e), 404, e)
            finally:
                ItemLayer.stock_remains_update()
