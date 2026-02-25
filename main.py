from fastapi import FastAPI
from recommender import recomendar_producto
from stock_service import sugerir_reposicion
from demand_service import predecir_demanda

app = FastAPI(title="IA Inventario — Proyecto de Grado")

@app.get("/")
def home():
    return {"mensaje": "Servicio IA funcionando"}

@app.get("/recomendar/{producto_id}")
def recomendar(producto_id: int):
    return recomendar_producto(producto_id)

@app.get("/reposicion")
def reposicion():
    return sugerir_reposicion()

@app.get("/prediccion")
def prediccion():
    return predecir_demanda()