from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from controllers.routing import StocksRouters, CitiesRouters
from storage.models import create_all_tables


class App(FastAPI):

    @staticmethod
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_all_tables()
        yield

    def __init__(self):
        super().__init__(
            title="StockController",
            version="0.0.1",
            lifespan=self.lifespan
        )
        self.setup_routers()

    def setup_routers(self):
        stocks = StocksRouters()
        stocks.setup_routers()
        cities = CitiesRouters()
        cities.setup_routers()

        @self.get("/")
        def root():
            return {"message": "Hello World"}

        self.include_router(stocks, prefix="/api", tags=["Stocks"])
        self.include_router(cities, prefix="/api", tags=["Cities"])


app = App()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)



