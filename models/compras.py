import psycopg2
from config import db_params

def registrar_compra(detalle, valor):
    if not valor:
        valor = 0.0

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Insertar compra
    cur.execute("INSERT INTO compras (detalle, valor) VALUES (%s, %s)", (detalle, valor))

    conn.commit()
    cur.close()
    conn.close()

def get_compras():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT id_compra, fecha, detalle, valor FROM compras ORDER BY fecha DESC")
    compras = cur.fetchall()
    cur.close()
    conn.close()
    return compras

def get_compra_por_id(id_compra):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT id_compra, fecha, detalle, valor FROM compras WHERE id_compra = %s", (id_compra,))
    compra = cur.fetchone()
    cur.close()
    conn.close()
    return compra

def editar_compra(id_compra, detalle, valor):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("UPDATE compras SET detalle = %s, valor = %s WHERE id_compra = %s",
                (detalle, valor, id_compra))

    conn.commit()
    cur.close()
    conn.close()

def eliminar_compra(id_compra):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("DELETE FROM compras WHERE id_compra = %s", (id_compra,))

    conn.commit()
    cur.close()
    conn.close()

def get_compras_por_rango(fecha_inicio, fecha_fin):
    """
    Devuelve las compras cuyo campo 'fecha' esté entre fecha_inicio y fecha_fin (inclusive).
    Se espera fecha_inicio y fecha_fin como 'YYYY-MM-DD' (strings).
    """
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Hacemos el rango inclusivo: desde 00:00:00 del inicio hasta 23:59:59 del fin
    inicio_ts = f"{fecha_inicio} 00:00:00"
    fin_ts = f"{fecha_fin} 23:59:59"

    cur.execute("""
        SELECT id_compra, fecha, detalle, valor
        FROM compras
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
    """, (inicio_ts, fin_ts))

    compras = cur.fetchall()
    cur.close()
    conn.close()
    return compras
