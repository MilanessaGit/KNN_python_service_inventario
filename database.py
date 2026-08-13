import os
import mysql.connector
import pandas as pd


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_DATABASE", "back_api_laravel")
    )

def get_product_data():
    """
    Obtiene los datos mínimos que necesita el módulo KNN.

    El stock real del sistema se calcula desde lotes.cantidad_actual.
    No se usa almacen_lote porque pertenece a una estructura anterior.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT
            p.id,
            p.categoria_id,
            p.precio_sugerido,
            COALESCE(SUM(l.cantidad_actual), 0) AS stock_total
        FROM productos p
        LEFT JOIN lotes l ON l.producto_id = p.id
        GROUP BY
            p.id,
            p.categoria_id,
            p.precio_sugerido
        ORDER BY p.id
        """

        cursor.execute(query)
        filas = cursor.fetchall()

        return pd.DataFrame(
            filas,
            columns=[
                "id",
                "categoria_id",
                "precio_sugerido",
                "stock_total"
            ]
        )
    finally:
        cursor.close()
        conn.close()
