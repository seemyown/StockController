import uvicorn
from fastapi import FastAPI

from controllers.routing import StocksRouters


class App(FastAPI):
    def __init__(self):
        super().__init__(
            title="StockController",
            version="0.0.1",
        )
        self.setup()

    def setup(self):
        stocks = StocksRouters()
        stocks.setup()

        @self.get("/")
        def root():
            return {"message": "Hello World"}

        self.include_router(stocks, prefix="/api")


app = App()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)



