from flask import Flask, render_template, request, redirect, url_for, flash
from models import clientes, inventario, ventas, compras, graficos
import psycopg2
from config import db_params
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"  # Necesario para usar flash()

# Inicio
@app.route("/")
def inicio():
    return render_template("dashboard.html")


# Inventario
@app.route("/inventario")
def inventario_view():
    productos = inventario.get_inventario()

    # Para la tabla y gráfico de inventario
    nombres = [p[1] for p in productos]  # nombre
    stock = [p[2] for p in productos]    # stock

    # Para gráfico de ventas por cliente y por producto (datos generales)
    registros = ventas.get_ventas()
    clientes_grafico = [r[1] for r in registros]           # nombre cliente
    subtotales_clientes = [r[5] for r in registros]        # subtotal (según get_ventas estructura)
    productos_ventas = [r[2] for r in registros]           # nombre producto
    subtotales_productos = [r[5] for r in registros]       # subtotal

    return render_template(
        "inventario.html",
        productos=productos,
        nombres=nombres,
        stock=stock,
        clientes=clientes_grafico,
        subtotales_clientes=subtotales_clientes,
        productos_ventas=productos_ventas,
        subtotales_productos=subtotales_productos
    )


@app.route("/inventario/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        try:
            cantidad = int(request.form["cantidad"])
            precio = float(request.form["precio"])
        except ValueError:
            error = "Cantidad y precio deben ser números válidos."
            return render_template("nuevo_producto.html", error=error)

        inventario.insertar_producto(nombre, cantidad, precio)
        flash("✅ Producto agregado correctamente")
        return redirect(url_for("inventario_view"))

    return render_template("nuevo_producto.html")


@app.route("/inventario/editar/<int:id_producto>", methods=["GET", "POST"])
def editar_producto(id_producto):
    if request.method == "POST":
        nuevo_nombre = request.form["nombre"]
        try:
            nueva_cantidad = int(request.form["cantidad"])
            nuevo_precio = float(request.form["precio"])
        except ValueError:
            error = "Cantidad y precio deben ser números válidos."
            producto = inventario.get_producto_por_id(id_producto)
            return render_template("editar_producto.html", producto=producto, error=error)

        inventario.actualizar_producto(id_producto, nuevo_nombre, nueva_cantidad, nuevo_precio)
        flash("✏️ Producto editado correctamente")
        return redirect(url_for("inventario_view"))

    producto = inventario.get_producto_por_id(id_producto)
    return render_template("editar_producto.html", producto=producto)


@app.route("/inventario/eliminar/<int:id_producto>", methods=["POST"])
def eliminar_producto(id_producto):
    inventario.eliminar_producto(id_producto)
    flash("🗑️ Producto eliminado correctamente")
    return redirect(url_for("inventario_view"))


# Ventas (unificada: registro y filtro por fechas)
@app.route("/ventas", methods=["GET", "POST"])
def ventas_view():
    error = None
    registros = []
    dinero_actual = ventas.get_dinero_actual()
    clientes_lista = clientes.get_clientes()
    productos_formulario = inventario.get_inventario()

    # POST para registrar venta (formulario de nueva venta)
    if request.method == "POST" and "cliente" in request.form and "producto" in request.form:
        try:
            id_cliente = int(request.form["cliente"])
            id_producto = int(request.form["producto"])
            cantidad = int(request.form["cantidad"])
        except (KeyError, ValueError):
            error = "Datos de venta inválidos."
            registros = ventas.get_historial()
        else:
            try:
                ventas.registrar_venta(id_cliente, id_producto, cantidad)
                flash("✅ Venta registrada correctamente")
                return redirect(url_for("ventas_view"))
            except Exception as e:
                error = str(e)
                # mostrar historial para contexto
                registros = ventas.get_historial()

    # POST para filtrar por rango de fechas (formulario de filtro)
    elif request.method == "POST" and "fecha_inicio" in request.form and "fecha_fin" in request.form:
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]
        # Asumimos que ventas.get_historial_por_rango existe y recibe strings 'YYYY-MM-DD'
        registros = ventas.get_historial_por_rango(fecha_inicio, fecha_fin)

    # GET o sin filtros: mostrar historial completo
    else:
        registros = ventas.get_historial()

    # Datos para gráfico (ajustar índices según la estructura devuelta por get_historial)
    # get_historial devuelve: (id_detalle, v.fecha, c.nombre, p.nombre, d.cantidad, p.precio, d.subtotal)
    productos_grafico = [fila[3] for fila in registros]
    subtotales_grafico = [fila[6] for fila in registros]

    return render_template(
        "ventas.html",
        clientes=clientes_lista,
        productos=productos_formulario,
        registros=registros,
        dinero_actual=dinero_actual,
        productos_grafico=productos_grafico,
        subtotales=subtotales_grafico,
        error=error
    )


# Editar venta (solo cantidad)
@app.route("/ventas/editar/<int:id_detalle>", methods=["GET", "POST"])
def editar_venta(id_detalle):
    if request.method == "POST":
        try:
            nueva_cantidad = int(request.form["cantidad"])
        except (KeyError, ValueError):
            return "Cantidad inválida", 400

        try:
            # Asumimos que ventas.editar_detalle_venta acepta (id_detalle, nueva_cantidad)
            ventas.editar_detalle_venta(id_detalle, nueva_cantidad)
            flash("✏️ Venta editada correctamente")
        except Exception as e:
            return f"Error al editar venta: {e}", 500

        return redirect(url_for("ventas_view"))

    detalle = ventas.get_detalle_por_id(id_detalle)
    clientes_lista = clientes.get_clientes()
    productos_lista = inventario.get_inventario()
    return render_template("editar_venta.html", detalle=detalle,
                           clientes=clientes_lista, productos=productos_lista)


# Eliminar venta
@app.route("/ventas/eliminar/<int:id_detalle>", methods=["POST"])
def eliminar_venta(id_detalle):
    try:
        ventas.eliminar_detalle_venta(id_detalle)
        flash("🗑️ Venta eliminada correctamente")
    except Exception as e:
        return f"Error al eliminar venta: {e}", 500
    return redirect(url_for("ventas_view"))


# Verificar conexión
@app.route("/test-db")
def test_db():
    try:
        import os, psycopg2
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clientes;")
        count = cur.fetchone()[0]
        conn.close()
        return {"clientes_registrados": count}
    except Exception as e:
        return {"error": str(e)}


@app.route("/clientes")
def clientes_listado():
    try:
        registros = clientes.get_clientes()
        return render_template("clientes.html", registros=registros)
    except Exception as e:
        return {"error": str(e)}

@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":
        clientes.insertar_cliente(request.form["nombre"], request.form["correo"], request.form["telefono"])
        flash("✅ Cliente agregado correctamente")
        return redirect(url_for("clientes_listado"))
    return render_template("nuevo_cliente.html")


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    if request.method == "POST":
        clientes.actualizar_cliente(id_cliente, request.form["nombre"], request.form["correo"], request.form["telefono"])
        flash("✏️ Cliente editado correctamente")
        return redirect(url_for("clientes_listado"))
    cliente = clientes.get_cliente_por_id(id_cliente)
    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
def eliminar_cliente(id_cliente):
    clientes.eliminar_cliente(id_cliente)
    flash("🗑️ Cliente eliminado correctamente")
    return redirect(url_for("clientes_listado"))


# Compras
@app.route("/compras", methods=["GET", "POST"])
def compras_view():
    error = None
    registros = []
    dinero_actual = ventas.get_dinero_actual()  # reutilizamos la función que ya tienes

    # Determinar acción enviada por el formulario (registro o filtro)
    action = request.form.get("action") if request.method == "POST" else None

    # Registrar nueva compra
    if request.method == "POST" and action == "purchase":
        detalle = request.form.get("detalle", "").strip()
        try:
            valor = float(request.form.get("valor", 0))
        except (TypeError, ValueError):
            error = "Valor inválido. Ingrese un número."
            registros = compras.get_compras()
        else:
            try:
                compras.registrar_compra(detalle, valor)
                flash("✅ Compra registrada correctamente")
                return redirect(url_for("compras_view"))
            except Exception as e:
                error = f"Error al registrar compra: {e}"
                registros = compras.get_compras()

    # Filtrar por rango de fechas
    elif request.method == "POST" and action == "filter":
        fecha_inicio = request.form.get("fecha_inicio", "").strip()
        fecha_fin = request.form.get("fecha_fin", "").strip()
        if not fecha_inicio or not fecha_fin:
            error = "Debe seleccionar fecha inicio y fecha fin."
            registros = compras.get_compras()
        else:
            try:
                registros = compras.get_compras_por_rango(fecha_inicio, fecha_fin)
            except Exception as e:
                error = f"Error al filtrar: {e}"
                registros = compras.get_compras()

    # GET o sin acción: mostrar historial completo
    else:
        registros = compras.get_compras()

    return render_template("compras.html",
                           registros=registros,
                           dinero_actual=dinero_actual,
                           error=error)


# Editar compra
@app.route("/compras/editar/<int:id_compra>", methods=["GET", "POST"])
def editar_compra(id_compra):
    if request.method == "POST":
        detalle = request.form["detalle"]
        try:
            valor = float(request.form["valor"])
        except ValueError:
            return "Valor inválido", 400

        try:
            compras.editar_compra(id_compra, detalle, valor)
            flash("✏️ Compra editada correctamente")
        except Exception as e:
            return f"Error al editar compra: {e}", 500
        return redirect(url_for("compras_view"))

    compra = compras.get_compra_por_id(id_compra)
    return render_template("editar_compra.html", compra=compra)


# Eliminar compra
@app.route("/compras/eliminar/<int:id_compra>", methods=["POST"])
def eliminar_compra(id_compra):
    try:
        compras.eliminar_compra(id_compra)
    except Exception as e:
        return f"Error al eliminar compra: {e}", 500
    return redirect(url_for("compras_view"))


# Gráficos
@app.route("/graficos")
def graficos_view():
    datos_clientes = graficos.ventas_por_cliente()
    datos_productos = graficos.ventas_por_producto()
    datos_compras = graficos.compras_totales()
    dinero_actual = graficos.dinero_actual()

    return render_template(
        "graficos.html",
        datos_clientes=datos_clientes,
        datos_productos=datos_productos,
        datos_compras=datos_compras,
        dinero_actual=dinero_actual
    )


# Ingresar stock y historial
@app.route("/inventario/ingresar_stock/<int:id_producto>", methods=["GET", "POST"])
def ingresar_stock_view(id_producto):
    if request.method == "POST":
        try:
            cantidad = int(request.form["cantidad"])
        except ValueError:
            return "Cantidad inválida", 400
        inventario.ingresar_stock(id_producto, cantidad)
        flash("✅ Stock ingresado correctamente")
        return redirect(url_for("inventario_view"))

    producto = inventario.get_producto_por_id(id_producto)
    return render_template("ingresar_stock.html", producto=producto)


@app.route("/inventario/historial_stock", methods=["GET", "POST"])
def historial_stock_view():
    historial = []
    if request.method == "POST" and "fecha_inicio" in request.form and "fecha_fin" in request.form:
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]
        historial = inventario.get_historial_stock_por_rango(fecha_inicio, fecha_fin)
    else:
        historial = inventario.get_historial_stock()  # por defecto muestra todo

    return render_template("historial_stock.html", historial=historial)


# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
