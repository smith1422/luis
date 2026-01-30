import psycopg2
from config import db_params

def get_clientes():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT id_cliente, nombre, correo, telefono FROM clientes ORDER BY id_cliente;")
    registros = cur.fetchall()
    cur.close()
    conn.close()
    return registros

def insertar_cliente(nombre, correo, telefono):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s);",
                (nombre, correo, telefono))
    conn.commit()
    cur.close()
    conn.close()

def actualizar_cliente(id_cliente, nombre, correo, telefono):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""UPDATE clientes SET nombre=%s, correo=%s, telefono=%s WHERE id_cliente=%s;""",
                (nombre, correo, telefono, id_cliente))
    conn.commit()
    cur.close()
    conn.close()

def eliminar_cliente(id_cliente):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ventas WHERE id_cliente=%s;", (id_cliente,))
    count = cur.fetchone()[0]
    if count > 0:
        raise Exception("No se puede eliminar: cliente con ventas registradas")
    cur.execute("DELETE FROM clientes WHERE id_cliente=%s;", (id_cliente,))
    conn.commit()
    cur.close()
    conn.close()



import psycopg2
from config import db_params

def get_cliente_por_id(id_cliente):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        SELECT id_cliente, nombre, correo, telefono
        FROM clientes
        WHERE id_cliente = %s
    """, (id_cliente,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()
    return cliente
