from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func
import models, schemas

# ==========================================
# INFRAESTRUCTURA
# ==========================================
def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion

def listar_estaciones(db: Session):
    return db.query(models.EstacionDB).all()

# ==========================================
# TELEMETRÍA
# ==========================================
def registrar_lectura(db: Session, lectura: schemas.LecturaCreate):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
        
    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura guardada en DB"}

# ==========================================
# REPORTES Y AUDITORÍA
# ==========================================
def obtener_riesgo(db: Session, estacion_id: int):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
        
    lecturas = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == estacion_id).all()
    if not lecturas:
        return {"id": estacion_id, "nivel": "SIN DATOS", "valor": 0}
        
    ultima_lectura = lecturas[-1].valor
    if ultima_lectura > 20.0:
        nivel = "PELIGRO"
    elif ultima_lectura > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    return {"id": estacion_id, "valor": ultima_lectura, "nivel": nivel}

def obtener_historial(db: Session, estacion_id: int):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    lecturas = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == estacion_id).all()
    valores = [l.valor for l in lecturas]
    
    conteo = len(valores)
    promedio = sum(valores) / conteo if conteo > 0 else 0.0

    return {
        "estacion_id": estacion_id,
        "nombre": estacion.nombre,
        "conteo": conteo,
        "promedio": round(promedio, 2),
        "lecturas": valores
    }

def reporte_critico(db: Session, umbral: float):
    criticas = db.query(models.LecturaDB).filter(models.LecturaDB.valor > umbral).all()
    return {
        "politica_umbral": umbral,
        "total_alertas": len(criticas),
        "datos": criticas
    }

def obtener_stats_globales(db: Session):
    total_e = db.query(models.EstacionDB).count()
    total_l = db.query(models.LecturaDB).count()
    
    todas = db.query(models.LecturaDB).all()
    promedio = sum([l.valor for l in todas]) / total_l if total_l > 0 else 0.0
    
    # Identificamos la estación más activa (la de lectura más alta)
    estacion_activa = None
    if total_l > 0:
        lectura_max = db.query(models.LecturaDB).order_by(models.LecturaDB.valor.desc()).first()
        if lectura_max:
            estacion_activa = lectura_max.estacion_id
            
    return {
        "total_estaciones": total_e,
        "total_lecturas": total_l,
        "promedio_general": round(promedio, 2),
        "estacion_mas_activa": estacion_activa
    }