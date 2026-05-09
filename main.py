from fastapi import FastAPI

from routes.clients import router as clients_router
from routes.addresses import router as addresses_router
from routes.products import router as products_router

app = FastAPI(title="Catalogs Service")
app.include_router(clients_router)
app.include_router(addresses_router)
app.include_router(products_router)


@app.get("/health")
def health():
    return {"status": "ok"}
