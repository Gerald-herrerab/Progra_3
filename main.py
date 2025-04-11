from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Personaje, Mision
from schemas import PersonajeCreate, MisionCreate
from cola import ColaMisiones

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependencia de sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Diccionario de colas por personaje_id
colas_personajes = {}

# Crear nuevo personaje
@app.post("/personajes")
def crear_personaje(personaje: PersonajeCreate, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=personaje.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Crear nueva misión
@app.post("/misiones")
def crear_mision(mision: MisionCreate, db: Session = Depends(get_db)):
    nueva = Mision(descripcion=mision.descripcion, xp=mision.xp)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Aceptar una misión (encolar en la cola del personaje)
@app.post("/personajes/{id_personaje}/misiones/{id_mision}")
def aceptar_mision(id_personaje: int, id_mision: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == id_personaje).first()
    mision = db.query(Mision).filter(Mision.id == id_mision).first()

    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrada")

    # Relación muchos a muchos (solo si no la tiene ya)
    if mision not in personaje.misiones:
        personaje.misiones.append(mision)
        db.commit()

    # Crear cola para el personaje si no existe
    if id_personaje not in colas_personajes:
        colas_personajes[id_personaje] = ColaMisiones()

    # Encolar la misión (solo si no está repetida)
    if mision not in colas_personajes[id_personaje].items:
        colas_personajes[id_personaje].enqueue(mision)

    return {"mensaje": f"Misión '{mision.descripcion}' aceptada por '{personaje.nombre}'."}

# Completar la primera misión en la cola (desencolar)
@app.post("/personajes/{id_personaje}/completar")
def completar_mision(id_personaje: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == id_personaje).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = colas_personajes.get(id_personaje)
    if not cola or cola.is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones en la cola")

    mision = cola.dequeue()
    personaje.experiencia += mision.xp
    db.commit()

    return {
        "mensaje": f"Misión completada: {mision.descripcion}",
        "xp_ganada": mision.xp,
        "experiencia_total": personaje.experiencia
    }

# Listar misiones en la cola del personaje
@app.get("/personajes/{id_personaje}/misiones")
def listar_misiones(id_personaje: int):
    cola = colas_personajes.get(id_personaje)
    if not cola or cola.is_empty():
        return {"misiones": []}

    return {
        "misiones": [
            {"id": m.id, "descripcion": m.descripcion, "xp": m.xp}
            for m in cola.items
        ]
    }
