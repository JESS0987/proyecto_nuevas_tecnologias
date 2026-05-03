"""
API REST - Tienda de Bisutería
Conecta el frontend (index.html) con la base de datos SQLite existente.
Despliega en Railway: configura DATABASE_PATH como variable de entorno si es necesario.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys, os

# Asegurarse de que el módulo app sea encontrado
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventario-mvc"))

from app.Models.database import Database
from app.Models.producto_model import ProductoModel
from app.Models.pedido_model import PedidoModel

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend HTML

# Inicializar DB al arrancar
Database.initialize()

# ──────────────────────────────────────────────────────────────────────────────
# PRODUCTOS
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/productos", methods=["GET"])
def listar_productos():
    """Devuelve todos los productos activos con stock > 0."""
    termino = request.args.get("q", "").strip()
    if termino:
        rows = ProductoModel.buscar(termino)
    else:
        rows = ProductoModel.obtener_todos(solo_activos=True)

    productos = []
    for r in rows:
        p = dict(r)
        if p.get("stock", 0) > 0:
            productos.append(p)
    return jsonify(productos)


@app.route("/api/productos/<int:pid>", methods=["GET"])
def detalle_producto(pid):
    row = ProductoModel.obtener_por_id(pid)
    if not row:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(dict(row))


# ──────────────────────────────────────────────────────────────────────────────
# CLIENTES
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    rows = PedidoModel.obtener_clientes()
    return jsonify([dict(r) for r in rows])


@app.route("/api/clientes", methods=["POST"])
def crear_cliente():
    data = request.get_json(force=True)
    nombre    = data.get("nombre", "").strip()
    documento = data.get("documento", "")
    telefono  = data.get("telefono", "")
    email     = data.get("email", "")
    direccion = data.get("direccion", "")

    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400

    try:
        cliente_id = PedidoModel.crear_cliente(
            nombre, documento, telefono, email, direccion
        )
        return jsonify({"id": cliente_id, "nombre": nombre}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ──────────────────────────────────────────────────────────────────────────────
# PEDIDOS / FACTURAS
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/pedidos", methods=["POST"])
def crear_pedido():
    """
    Body JSON esperado:
    {
      "cliente_id": 1,
      "items": [
        { "producto_id": 3, "cantidad": 2, "precio_unitario": 10000, "costo_unitario": 4000 }
      ],
      "descuento": 0,
      "notas": ""
    }
    """
    data = request.get_json(force=True)

    cliente_id = data.get("cliente_id")
    items      = data.get("items", [])
    descuento  = float(data.get("descuento", 0))
    notas      = data.get("notas", "")

    if not cliente_id:
        return jsonify({"error": "cliente_id es requerido"}), 400
    if not items:
        return jsonify({"error": "El pedido debe tener al menos un ítem"}), 400

    # Validar stock antes de procesar
    for item in items:
        prod = ProductoModel.obtener_por_id(item["producto_id"])
        if not prod:
            return jsonify({"error": f"Producto {item['producto_id']} no existe"}), 400
        if prod["stock"] < item["cantidad"]:
            return jsonify({
                "error": f"Stock insuficiente para '{prod['nombre']}'. "
                         f"Disponible: {prod['stock']}, solicitado: {item['cantidad']}"
            }), 400

    try:
        numero_factura = PedidoModel.crear_pedido(
            cliente_id=cliente_id,
            items=items,
            descuento=descuento,
            notas=notas,
            estado="pendiente",
        )
        # Recuperar pedido completo para devolverlo
        pedido, items_det = PedidoModel.obtener_por_numero(numero_factura)
        return jsonify({
            "numero_factura": numero_factura,
            "pedido": dict(pedido) if pedido else {},
            "items": [dict(i) for i in items_det],
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pedidos/<string:num_factura>", methods=["GET"])
def detalle_pedido(num_factura):
    pedido, items = PedidoModel.obtener_por_numero(num_factura)
    if not pedido:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify({
        "pedido": dict(pedido),
        "items": [dict(i) for i in items],
    })


@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    rows = PedidoModel.obtener_todos(limite=100)
    return jsonify([dict(r) for r in rows])


# ──────────────────────────────────────────────────────────────────────────────
# FRONTEND — sirve index.html y archivos estáticos
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Sirve el frontend de la tienda."""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "Bisutería Inventario API"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
