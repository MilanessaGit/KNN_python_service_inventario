from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = FastAPI()

# Datos simulados (pueden venir de tu BD luego)
productos = [
    [50, 120, 80],   # peso, largo, ancho
    [55, 125, 82],
    [30, 90, 60],
    [80, 200, 100],
    [28, 88, 58]
]

modelo = NearestNeighbors(n_neighbors=3)
modelo.fit(productos)


class Producto(BaseModel):
    peso: float
    largo: float
    ancho: float


@app.post("/recomendar")
def recomendar(prod: Producto):

    nuevo = np.array([[prod.peso, prod.largo, prod.ancho]])

    distancias, indices = modelo.kneighbors(nuevo)

    recomendaciones = [productos[i] for i in indices[0]]

    return {
        "producto_consultado": nuevo.tolist(),
        "recomendaciones": recomendaciones
    }
