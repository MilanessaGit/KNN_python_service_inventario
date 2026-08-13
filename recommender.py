import pandas as pd
from sklearn.neighbors import NearestNeighbors
from database import get_product_data


def recomendar_producto(producto_id, k=5):
    """
    Recomienda productos similares mediante KNN.

    Criterios actuales:
    - La categoría se usa como filtro previo.
    - El precio_sugerido es la característica numérica del KNN.
    - El stock se usa únicamente como filtro de disponibilidad.
    - El producto seleccionado nunca se recomienda a sí mismo.

    Esta implementación puede ampliarse posteriormente con material,
    peso, color, gama, dimensiones u otras características.
    """

    df = get_product_data()

    if df.empty:
        return {"error": "No existen productos registrados"}

    # Asegurar tipos numéricos para evitar problemas con MySQL/Pandas.
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["categoria_id"] = pd.to_numeric(df["categoria_id"], errors="coerce")
    df["precio_sugerido"] = pd.to_numeric(
        df["precio_sugerido"], errors="coerce"
    ).fillna(0.0)
    df["stock_total"] = pd.to_numeric(
        df["stock_total"], errors="coerce"
    ).fillna(0)

    producto_id = int(producto_id)

    if producto_id not in df["id"].values:
        return {"error": "Producto no encontrado"}

    # Producto que servirá como referencia.
    producto = df[df["id"] == producto_id].iloc[0]
    precio_base = float(producto["precio_sugerido"])
    categoria_base = producto["categoria_id"]

    if precio_base <= 0:
        return {"error": "El producto no tiene un precio sugerido válido"}

    # Candidatos:
    # - misma categoría
    # - distintos del producto seleccionado
    # - con stock disponible
    # - con precio válido
    candidatos = df[
        (df["categoria_id"] == categoria_base)
        & (df["id"] != producto_id)
        & (df["stock_total"] > 0)
        & (df["precio_sugerido"] > 0)
    ].copy()

    if candidatos.empty:
        return {
            "error": "No hay productos similares con stock disponible en esta categoría"
        }

    cantidad_vecinos = min(int(k), len(candidatos))

    # Por ahora KNN utiliza solamente precio_sugerido.
    # Al tener una sola característica no es necesario StandardScaler.
    caracteristicas = candidatos[["precio_sugerido"]]

    modelo = NearestNeighbors(
        n_neighbors=cantidad_vecinos,
        metric="euclidean"
    )
    modelo.fit(caracteristicas)

    producto_consulta = pd.DataFrame(
        [[precio_base]],
        columns=["precio_sugerido"]
    )

    distancias, indices = modelo.kneighbors(producto_consulta)

    recomendaciones = candidatos.iloc[indices[0]].copy()
    recomendaciones["distancia_precio"] = distancias[0]

    # Convertimos explícitamente a tipos simples para que FastAPI
    # pueda serializar la respuesta sin problemas.
    resultado = []

    for _, producto_recomendado in recomendaciones.iterrows():
        resultado.append({
            "id": int(producto_recomendado["id"]),
            "categoria_id": int(producto_recomendado["categoria_id"]),
            "precio_sugerido": float(producto_recomendado["precio_sugerido"]),
            "stock_total": int(producto_recomendado["stock_total"]),
            "distancia_precio": float(producto_recomendado["distancia_precio"])
        })

    return resultado
