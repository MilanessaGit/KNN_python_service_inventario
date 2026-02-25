import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="back_api_laravel"
    )

def get_product_data():
    conn = get_connection()

    query = """
    SELECT
        p.id,
        p.categoria_id,
        p.precio_sugerido,
        p.peso,
        COALESCE(SUM(al.cantidad),0) AS stock_total
    FROM productos p
    LEFT JOIN lotes l ON l.producto_id = p.id
    LEFT JOIN almacen_lote al ON al.lote_id = l.id
    GROUP BY p.id
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df