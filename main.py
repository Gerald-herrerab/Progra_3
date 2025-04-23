from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from base import SessionLocal, engine
from modelos import Base, Vuelo
from tda_lista import ListaDoblementeEnlazada  # Importa la lista doblemente enlazada

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Instancia de la lista doblemente enlazada
lista_vuelos = ListaDoblementeEnlazada()

# Modelo de Pydantic para validar datos de entrada
class VueloInput(BaseModel):
    origen: str
    destino: str

# Dependencia para obtener sesión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE vuelo
@app.post("/vuelos/")
def crear_vuelo(vuelo: VueloInput, db: Session = Depends(get_db)):
    nuevo = Vuelo(**vuelo.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# READ todos los vuelos
@app.get("/vuelos/")
def listar_vuelos(db: Session = Depends(get_db)):
    return db.query(Vuelo).all()

# READ vuelo por ID
@app.get("/vuelos/{vuelo_id}")
def obtener_vuelo(vuelo_id: int, db: Session = Depends(get_db)):
    vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

# UPDATE vuelo
@app.put("/vuelos/{vuelo_id}")
def actualizar_vuelo(vuelo_id: int, datos: VueloInput, db: Session = Depends(get_db)):
    vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    for key, value in datos.dict().items():
        setattr(vuelo, key, value)
    db.commit()
    db.refresh(vuelo)
    return vuelo

# DELETE vuelo
@app.delete("/vuelos/{vuelo_id}")
def eliminar_vuelo(vuelo_id: int, db: Session = Depends(get_db)):
    vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    db.delete(vuelo)
    db.commit()
    return {"ok": True}

# Agregar vuelo al frente de la lista (emergencia)
@app.post("/vuelos_emergencia/")
def agregar_vuelo_emergencia(vuelo: VueloInput):
    lista_vuelos.insertar_al_frente(vuelo.dict())
    return {"mensaje": "Vuelo agregado al frente", "vuelo": vuelo}

# Agregar vuelo al final de la lista (regular)
@app.post("/vuelos_regulares/")
def agregar_vuelo_regular(vuelo: VueloInput):
    lista_vuelos.insertar_al_final(vuelo.dict())
    return {"mensaje": "Vuelo agregado al final", "vuelo": vuelo}

# Obtener el primer vuelo de la lista
@app.get("/vuelos/primero/")
def obtener_primer_vuelo():
    vuelo = lista_vuelos.obtener_primero()
    if vuelo is None:
        raise HTTPException(status_code=404, detail="No hay vuelos en la lista")
    return {"vuelo": vuelo}

# Obtener el último vuelo de la lista
@app.get("/vuelos/ultimo/")
def obtener_ultimo_vuelo():
    vuelo = lista_vuelos.obtener_ultimo()
    if vuelo is None:
        raise HTTPException(status_code=404, detail="No hay vuelos en la lista")
    return {"vuelo": vuelo}

# Obtener la longitud de la lista
@app.get("/vuelos/longitud/")
def obtener_longitud_lista():
    return {"longitud": lista_vuelos.longitud()}

# Insertar vuelo en una posición específica
@app.post("/vuelos/posicion/")
def insertar_vuelo_en_posicion(vuelo: VueloInput, posicion: int):
    try:
        lista_vuelos.insertar_en_posicion(vuelo.dict(), posicion)
        return {"mensaje": f"Vuelo insertado en la posición {posicion}", "vuelo": vuelo}
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Extraer vuelo de una posición específica
@app.delete("/vuelos/posicion/{posicion}")
def extraer_vuelo_de_posicion(posicion: int):
    try:
        vuelo = lista_vuelos.extraer_de_posicion(posicion)
        return {"mensaje": f"Vuelo extraído de la posición {posicion}", "vuelo": vuelo}
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/debug_lista/")
def debug_lista():
    vuelos = []
    actual = lista_vuelos.cabeza
    while actual:
        vuelos.append(actual.vuelo)
        actual = actual.siguiente
    return {"vuelos": vuelos, "longitud": lista_vuelos.longitud()}
