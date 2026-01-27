import psycopg2
from config import db_params
from psycopg2.extras import RealDictCursor

def get_inventario():
    conn = psycopg2.connect(**db_params)
    conn.set_client_encoding('UTF8')
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id_producto, nombre, stock_actual, precio, stock_actual * 10 AS empanadas_totales
        FROM productos
        ORDER BY nombre;
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    productos = [(row['id_producto'], row['nombre'], row['stock_actual'], row['precio'], row['empanadas_totales']) for row in data]
    return productos

def insertar_producto(nombre, cantidad, precio):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO productos (nombre, stock_actual, precio) VALUES (%s, %s, %s)",
        (nombre, cantidad, precio)
    )
    conn.commit()
    cur.close()
    conn.close()

def actualizar_producto(id_producto, nombre, cantidad, precio):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        "UPDATE productos SET nombre = %s, stock_actual = %s, precio = %s WHERE id_producto = %s",
        (nombre, cantidad, precio, id_producto)
    )
    conn.commit()
    cur.close()
    conn.close()

def eliminar_producto(id_producto):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Primero eliminar las compras relacionadas
    cur.execute("DELETE FROM detalle_compra WHERE id_producto = %s", (id_producto,))

    # Luego eliminar las ventas relacionadas
    cur.execute("DELETE FROM detalle_venta WHERE id_producto = %s", (id_producto,))

    # Finalmente eliminar el producto
    cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conn.commit()

    cur.close()
    conn.close()



def get_producto_por_id(id_producto):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT id_producto, nombre, stock_actual, precio, stock_actual * 10 AS empanadas_totales
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))
    producto = cur.fetchone()
    cur.close()
    conn.close()
    return producto


def ingresar_stock(id_producto, cantidad):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Actualizar stock del producto
    cur.execute("UPDATE productos SET stock_actual = stock_actual + %s WHERE id_producto = %s",
                (cantidad, id_producto))

    # Registrar en historial
    cur.execute("INSERT INTO historial_stock (id_producto, cantidad) VALUES (%s, %s)",
                (id_producto, cantidad))

    conn.commit()
    cur.close()
    conn.close()

def get_historial_stock():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT h.id_ingreso, p.nombre, h.cantidad, h.fecha
        FROM historial_stock h
        JOIN productos p ON h.id_producto = p.id_producto
        ORDER BY h.fecha DESC
    """)
    historial = cur.fetchall()
    cur.close()
    conn.close()
    return historial

def get_historial_stock_por_rango(fecha_inicio, fecha_fin):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT h.id_ingreso, p.nombre, h.cantidad, h.fecha
        FROM historial_stock h
        JOIN productos p ON h.id_producto = p.id_producto
        WHERE h.fecha BETWEEN %s AND %s
        ORDER BY h.fecha DESC
    """, (fecha_inicio, fecha_fin))
    historial = cur.fetchall()
    cur.close()
    conn.close()
    return historial

