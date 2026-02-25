from database import get_product_data

def sugerir_reposicion(umbral=10):

    df = get_product_data()

    bajos = df[df["stock_total"] < umbral]

    return bajos[[
        "id",
        "categoria_id",
        "stock_total"
    ]].to_dict(orient="records")