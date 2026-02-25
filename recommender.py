import numpy as np
from sklearn.neighbors import NearestNeighbors
from database import get_product_data

def recomendar_producto(producto_id, k=5):

    df = get_product_data()

    if producto_id not in df["id"].values:
        return {"error": "Producto no encontrado"}

    # 🔹 Obtener producto base
    producto = df[df["id"] == producto_id].iloc[0]

    # 🔥 FILTRO POR CATEGORÍA
    misma_categoria = df[df["categoria_id"] == producto["categoria_id"]]

    if len(misma_categoria) <= 1:
        return {"error": "No hay suficientes productos en esta categoría"}

    # 🔹 Características para KNN
    df_features = misma_categoria[[
        "precio_sugerido",
        "peso",
        "stock_total"
    ]].fillna(0)

    modelo = NearestNeighbors(n_neighbors=min(k+1, len(misma_categoria)))
    modelo.fit(df_features)

    idx = misma_categoria.index[
        misma_categoria["id"] == producto_id
    ][0]

    distancias, indices = modelo.kneighbors([df_features.loc[idx]])

    recomendaciones = misma_categoria.iloc[indices[0][1:]]

    return recomendaciones[[
        "id",
        "categoria_id",
        "precio_sugerido",
        "stock_total"
    ]].to_dict(orient="records")