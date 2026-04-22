from pydantic import BaseModel, Field
from typing import Optional

class EstacionCreate(BaseModel):
    id: int = Field(..., example=1)
    nombre: str = Field(..., example="Río Yauli")
    ubicacion: str = Field(..., example="La Oroya")

class EstacionDB(EstacionCreate):
    class Config:
        orm_mode = True

class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float

class StatsResponse(BaseModel):
    total_estaciones: int
    total_lecturas: int
    promedio_general: float
    estacion_mas_activa: Optional[int]