from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Tabla intermedia para la relación muchos a muchos
personaje_mision = Table(
    'personaje_mision', Base.metadata,
    Column('personaje_id', ForeignKey('personajes.id'), primary_key=True),
    Column('mision_id', ForeignKey('misiones.id'), primary_key=True)
)

class Personaje(Base):
    __tablename__ = 'personajes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    experiencia = Column(Integer, default=0)
    misiones = relationship("Mision", secondary=personaje_mision, back_populates="personajes")

class Mision(Base):
    __tablename__ = 'misiones'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String)
    xp = Column(Integer)
    personajes = relationship("Personaje", secondary=personaje_mision, back_populates="misiones")
