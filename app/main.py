from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Importaciones de tus nuevos módulos (Clean Code)
import models
import schemas
import crud
from database import engine, get_db

# ==========================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# ==========================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
    API robusta para la gestión y monitoreo de desastres naturales.
    Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
    **Entidades principales:**
    * **Estaciones:** Puntos de monitoreo físico.
    * **Lecturas:** Datos capturados por sensores.
    * **Riesgos:** Análisis de criticidad basado en umbrales.
    """,
    version="1.0.0",
    terms_of_service="http://unmsm.edu.pe/terms/",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "url": "http://fisi.unmsm.edu.pe",
        "email": "desarrollo.smat@unmsm.edu.pe",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# ==========================================================
# MIDDLEWARE Y SEGURIDAD (CORS) - Laboratorio 4.3
# ==========================================================
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ENDPOINTS: GESTIÓN DE INFRAESTRUCTURA
# ==========================================================

@app.post(
    "/estaciones/",
    status_code=201,
    tags=["Gestión de Infraestructura"],
    summary="Registrar una nueva estación de monitoreo",
    description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
)
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    # Toda la lógica de guardado se movió a crud.py
    return crud.crear_estacion(db=db, estacion=estacion)

@app.get(
    "/estaciones/", 
    tags=["Gestión de Infraestructura"]
) 
def listar_estaciones(db: Session = Depends(get_db)):
    return crud.listar_estaciones(db=db)

# ==========================================================
# ENDPOINTS: TELEMETRÍA
# ==========================================================

@app.post(
    "/lecturas/",
    status_code=201,
    tags=["Telemetría de Sensores"],
    summary="Recibir datos de telemetría",
    description="Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante su ID."
)
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db)):
    return crud.registrar_lectura(db=db, lectura=lectura)

# ==========================================================
# ENDPOINTS: ANÁLISIS DE RIESGO Y REPORTES
# ==========================================================

@app.get(
    "/estaciones/{id}/riesgo",
    tags=["Análisis de Riesgo"],
    summary="Evaluar nivel de peligro actual",
    description="Analiza la última lectura recibida de una estación y determina si el estado es NORMAL, ALERTA o PELIGRO."
)
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    return crud.obtener_riesgo(db=db, estacion_id=id)

@app.get(
    "/estaciones/{id}/historial",
    tags=["Reportes Históricos"],
    summary="Obtener historial estadístico de una estación",
    description="""
    Realiza un análisis descriptivo de las lecturas capturadas por una estación específica. 
    Calcula el **conteo total** de registros y el **promedio aritmético** de los valores de los sensores.
    """,
    responses={404: {"description": "Estación no encontrada en los registros"}}
)
def obtener_historial(id: int, db: Session = Depends(get_db)):
    return crud.obtener_historial(db=db, estacion_id=id)

@app.get(
    "/reportes/criticos",
    tags=["Auditoría"],
    summary="Listado de lecturas que exceden el umbral",
    description="""
    Filtra la telemetría del sistema para identificar valores que representen un riesgo potencial. 
    El parámetro **umbral** es opcional; si no se especifica, el sistema asume una política de seguridad de **20.0**.
    """
)
def reporte_critico(umbral: float = Query(20.0, description="Límite técnico para filtrar alertas"), db: Session = Depends(get_db)):
    return crud.reporte_critico(db=db, umbral=umbral)

@app.get(
    "/estaciones/stats",
    tags=["Resumen Ejecutivo"],
    summary="Estado global del sistema SMAT",
    description="""
    Proporciona una visión gerencial del sistema. Consolida métricas de todas las estaciones registradas 
    para evaluar la carga de datos y el rendimiento general de la red de monitoreo.
    """,
    response_model=schemas.StatsResponse
)
def obtener_stats_globales(db: Session = Depends(get_db)):
    return crud.obtener_stats_globales(db=db)