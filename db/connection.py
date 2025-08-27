# db/connection.py
import sqlite3

DB_NAME = "beyond.db"

def get_connection():
    """
    Retorna una conexión a la base de datos SQLite.
    Usa row_factory para devolver resultados como diccionarios.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Permite acceder a los resultados como diccionario
    return conn


def execute_query(query, params=None):
    """
    Ejecuta un query de escritura (INSERT, UPDATE, DELETE).
    """
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()


def fetch_all(query, params=None):
    """
    Ejecuta un SELECT que retorna múltiples filas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_one(query, params=None):
    """
    Ejecuta un SELECT que retorna una sola fila.
    """
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    return row
