from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from cities.models import DbCity
from dependencies import app, get_db, fetch_temperature, ListDep
from temperatures import crud
from temperatures.models import DbTemperature
from temperatures.schemas import Temperature


@app.post("/temperatures/update")
async def update_temperatures(db: Session = Depends(get_db)) -> dict[str, str]:
    cities = db.query(DbCity).all()

    for city in cities:
        try:
            temp = await fetch_temperature(city.id, city.name)
            new_temperature = DbTemperature(
                city_id=city.id,
                date_time=datetime.now(),
                temperature=temp
            )
            db.add(new_temperature)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    db.commit()
    return {"message": "Temperatures updated successfully"}


@app.get("/temperatures")
def get_temperatures(commons: ListDep) -> List[Temperature]:
    return crud.get_temperatures(commons)


@app.get("/temperatures")
def get_city_temperatures(city_id: int, commons: ListDep) -> List[Temperature]:
    commons["q"] = city_id

    return crud.get_temperatures(commons)
