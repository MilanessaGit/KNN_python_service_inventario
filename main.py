from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.neighbors import NearestNeighbors
import mysql.connector

app = FastAPI()

# ===== MODELO DE ENTRADA =====
class ProductoInput(BaseModel):
    producto_id: int


# ===== FUNCIÓN PARA OBTENER PRODUCTOS DE LA BD =====
def obtener_productos():

    conexion = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",           # <-- Cambia si tienes contraseña
        database="back_api_laravel"  # <-- Cambia por el nombre real de tu BD
    )

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            id,
            peso,
            precio_sugerido,
            dimensiones,
            material,
            categoria_id
        FROM productos
        WHERE peso IS NOT NULL
          AND precio_sugerido IS NOT NULL
    """)

    resultados = cursor.fetchall()
    conexion.close()

    datos = []
    ids = []

    for r in resultados:

        id_p, peso, precio, dimensiones, material, categoria = r

        # ===== CONVERTIR DIMENSIONES (varchar -> números) =====
        largo = 0
        ancho = 0
        alto = 0

        if dimensiones:
            partes = dimensiones.replace(" ", "").lower().split("x")

            try:
                if len(partes) >= 1:
                    largo = float(partes[0])
                if len(partes) >= 2:
                    ancho = float(partes[1])
                if len(partes) >= 3:
                    alto = float(partes[2])
            except:
                pass

        # ===== CONVERTIR MATERIAL (texto -> número) =====
        material = material.lower() if material else ""

        if "madera" in material:
            mat = 1
        elif "mdf" in material:
            mat = 2
        elif "metal" in material:
            mat = 3
        elif "vidrio" in material:
            mat = 4
        else:
            mat = 0

        # ===== VECTOR NUMÉRICO DEL PRODUCTO =====
        vector = [
            float(peso),
            float(precio),
            largo,
            ancho,
            alto,
            mat,
            float(categoria) if categoria else 0
        ]

        datos.append(vector)
        ids.append(id_p)

    return np.array(datos), ids


# ===== ENDPOINT KNN =====
@app.post("/recomendar")
def recomendar(input: ProductoInput):

    X, ids = obtener_productos()

    if len(X) == 0:
        return {"error": "No hay datos suficientes"}

    # Buscar índice del producto solicitado
    if input.producto_id not in ids:
        return {"error": "Producto no encontrado"}

    idx = ids.index(input.producto_id)

    # Modelo KNN
    modelo = NearestNeighbors(n_neighbors=4)
    modelo.fit(X)

    distancias, indices = modelo.kneighbors([X[idx]])

    recomendados = []

    for i in indices[0]:
        if ids[i] != input.producto_id:
            recomendados.append(ids[i])

    return {
        "producto_consultado": input.producto_id,
        "productos_similares": recomendados
    }


# ===== ENDPOINT OPCIONAL: VER TODOS LOS PRODUCTOS CARGADOS =====
@app.get("/productos")
def listar_productos():
    X, ids = obtener_productos()
    return {
        "total_productos": len(ids),
        "ids": ids
    }