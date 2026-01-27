import psycopg2
from config import db_params

# Ventas agrupadas por cliente
def ventas_por_cliente():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.nombre, SUM(d.subtotal)
        FROM detalle_venta d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN clientes c ON v.id_cliente = c.id_cliente
        GROUP BY c.nombre
        ORDER BY SUM(d.subtotal) DESC
    """)
    datos = cur.fetchall()
    cur.close()
    conn.close()
    return datos

# Ventas agrupadas por producto
def ventas_por_producto():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT p.nombre, SUM(d.subtotal)
        FROM detalle_venta d
        JOIN productos p ON d.id_producto = p.id_producto
        GROUP BY p.nombre
        ORDER BY SUM(d.subtotal) DESC
    """)
    datos = cur.fetchall()
    cur.close()
    conn.close()
    return datos

# Compras registradas
def compras_totales():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT detalle, valor
        FROM compras
        ORDER BY fecha ASC
    """)
    datos = cur.fetchall()
    cur.close()
    conn.close()
    return datos

# Dinero actual = ventas - compras
def dinero_actual():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(total), 0) FROM ventas")
    total_ventas = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(valor), 0) FROM compras")
    total_compras = cur.fetchone()[0]

    cur.close()
    conn.close()
    return total_ventas - total_compras
