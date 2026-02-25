import pandas as pd
from database import get_connection

def predecir_demanda():

    conn = get_connection()

    query = """
    SELECT
        l.producto_id,
        SUM(lv.cantidad) AS total_vendido
    FROM lote_venta lv
    JOIN lotes l ON lv.lote_id = l.id
    GROUP BY l.producto_id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return {"mensaje": "No hay datos de ventas"}

    df["demanda_estimada"] = df["total_vendido"] * 1.2

    return df.to_dict(orient="records")