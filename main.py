import httpx
from fastapi import FastAPI, HTTPException
from config import settings
from enum import Enum
from fastapi import Query
from datetime import date
from typing import Literal

app = FastAPI(title="CDSE Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/token")
async def get_token():
    data = {
      "client_id": "cdse-public",
      "username": settings.cdse_username,
      "password": settings.cdse_password,
      "grant_type": "password",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(settings.token_url, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


class Satellite(str, Enum):
    sentinel1 = "SENTINEL-1"
    sentinel2 = "SENTINEL-2"
    sentinel3 = "SENTINEL-3"
    sentinel5 = "SENTINEL-5"
    sentinel6 = "SENTINEL-6"

@app.get("/products")
async def search_products(
    satellite: Satellite,
    product_name: str | None = Query(None, description="Product name, e.g. S1A"),
    start_date: date | None = Query(None, description="e.g. 2025-06-01"),
    end_date: date | None = Query(None, description="e.g. 2025-06-30"),
    publication_date_start: date | None = Query(None, description="Published after, e.g. 2025-06-30"),
    publication_date_end: date | None = Query(None, description="Published before, e.g. 2025-06-30"),
    top: int = Query(10, ge=1, le=100, description="Max number of results"),
    order_by: Literal["asc","desc"] = Query('asc', description="Sort by sensing date: asc = oldest first / desc = newst first"),
    count : bool = Query(False, description="Show how many products fit the search"),
):

    filters = [f"Collection/Name eq '{satellite.value}'"]

    if product_name:
        filters.append(f"contains(Name,'{product_name}')")
    if start_date:
        filters.append(f"ContentDate/Start gt {start_date}T00:00:00.000Z")
    if end_date:
        filters.append(f"ContentDate/Start lt {end_date}T23:59:59.999Z")
    if publication_date_start:
        filters.append(f"PublicationDate gt {publication_date_start}T00:00:00.000Z")
    if publication_date_end:
        filters.append(f"PublicationDate lt {publication_date_end}T23:59:59.999Z")

    params = {
        "$filter": " and ".join(filters),
        "$top": top,
        "$orderby": f"ContentDate/Start {order_by}",
    }
    if count:
        params["$count"] = "true"

    print("CDSE filter:", params["$filter"])

    # CDSE CALL
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{settings.catalogue_url}", params=params)

    # CDSE ERRORS
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)


    return response.json()