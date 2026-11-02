import httpx
from fastapi import FastAPI, HTTPException
from config import settings

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