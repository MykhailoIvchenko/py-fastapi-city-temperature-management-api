from database import SessionLocal
from fastapi import FastAPI, Depends
from typing import Annotated
import httpx
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def common_city_item_params(db: Session, city_id: int) -> dict:
    return {"db": db, "city_id": city_id}


def common_list_params(
        q: str | None,
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10
) -> dict:
    return {
        "db": db,
        "q": q,
        "skip": skip,
        "limit": limit
    }


ListDep = Annotated[dict, Depends(common_list_params)]

CityItemDep = Annotated[dict, Depends(common_city_item_params)]


async def fetch_temperature(city_id: int, city_name: str) -> float:
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city_name}&aqi=no"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["current"]["temp_c"]
