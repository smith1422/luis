import psycopg2
from config import db_params

def registrar_venta(id_cliente, id_producto, cantidad):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Verificar producto
    cur.execute("SELECT precio, stock_actual FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cur.fetchone()
    if not producto:
        cur.close()
        conn.close()
        raise Exception("El producto no existe en el inventario.")

    precio, stock_actual = producto

    if cantidad > stock_actual:
        cur.close()
        conn.close()
        raise Exception(f"Stock insuficiente. Disponible: {stock_actual}, solicitado: {cantidad}")

    subtotal = precio * cantidad

    # Insertar venta
    cur.execute("INSERT INTO ventas (id_cliente, total) VALUES (%s, %s) RETURNING id_venta",
                (id_cliente, subtotal))
    id_venta = cur.fetchone()[0]

    # Insertar detalle
    cur.execute("INSERT INTO detalle_venta (id_venta, id_producto, cantidad, subtotal) VALUES (%s, %s, %s, %s)",
                (id_venta, id_producto, cantidad, subtotal))

    # Actualizar inventario
    cur.execute("UPDATE productos SET stock_actual = stock_actual - %s WHERE id_producto = %s",
                (cantidad, id_producto))

    conn.commit()
    cur.close()
    conn.close()

def get_dinero_actual():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Suma de ventas
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM ventas")
    total_ventas = cur.fetchone()[0]

    # Suma de compras
    cur.execute("SELECT COALESCE(SUM(valor), 0) FROM compras")
    total_compras = cur.fetchone()[0]

    # Dinero actual = ventas - compras
    dinero = total_ventas - total_compras

    cur.close()
    conn.close()
    return dinero

def get_historial():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id_detalle, v.fecha, c.nombre, p.nombre, d.cantidad, p.precio, d.subtotal
        FROM detalle_venta d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN productos p ON d.id_producto = p.id_producto
        ORDER BY v.fecha DESC
    """)
    historial = cur.fetchall()
    cur.close()
    conn.close()
    return historial

def get_ventas():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id_venta, c.nombre, p.nombre, d.cantidad, p.precio, d.subtotal
        FROM detalle_venta d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN productos p ON d.id_producto = p.id_producto
        ORDER BY v.fecha DESC
    """)
    ventas = cur.fetchall()
    cur.close()
    conn.close()
    return ventas

def get_detalle_por_id(id_detalle):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id_detalle, v.id_venta, c.nombre, p.nombre, d.cantidad, p.precio, d.subtotal
        FROM detalle_venta d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN productos p ON d.id_producto = p.id_producto
        WHERE d.id_detalle = %s
    """, (id_detalle,))
    detalle = cur.fetchone()
    cur.close()
    conn.close()
    return detalle

def eliminar_detalle_venta(id_detalle):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Recuperar producto, cantidad y venta antes de borrar
    cur.execute("SELECT id_producto, cantidad, id_venta FROM detalle_venta WHERE id_detalle = %s", (id_detalle,))
    fila = cur.fetchone()
    if not fila:
        cur.close()
        conn.close()
        raise Exception("El detalle de venta no existe.")

    id_producto, cantidad, id_venta = fila

    # Devolver stock al inventario
    cur.execute("UPDATE productos SET stock_actual = stock_actual + %s WHERE id_producto = %s",
                (cantidad, id_producto))

    # Eliminar detalle
    cur.execute("DELETE FROM detalle_venta WHERE id_detalle = %s", (id_detalle,))

    # Recalcular total de la venta
    cur.execute("SELECT COALESCE(SUM(subtotal),0) FROM detalle_venta WHERE id_venta = %s", (id_venta,))
    nuevo_total = cur.fetchone()[0]
    cur.execute("UPDATE ventas SET total = %s WHERE id_venta = %s", (nuevo_total, id_venta))

    conn.commit()
    cur.close()
    conn.close()

def get_historial_por_rango(fecha_inicio, fecha_fin):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id_detalle, v.fecha, c.nombre, p.nombre, d.cantidad, p.precio, d.subtotal
        FROM detalle_venta d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN productos p ON d.id_producto = p.id_producto
        WHERE v.fecha BETWEEN %s AND %s
        ORDER BY v.fecha DESC
    """, (fecha_inicio, fecha_fin))
    historial = cur.fetchall()
    cur.close()
    conn.close()
    return historial
