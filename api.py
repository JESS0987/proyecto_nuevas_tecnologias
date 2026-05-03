"""
API REST - Tienda de Bisutería · Glamour
Detecta automáticamente si está en la raíz del repo o dentro de inventario-mvc/
"""

import os, sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ── Detección automática de rutas ──────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

if os.path.isdir(os.path.join(BASE, "app")):
    PROJECT_DIR = BASE
elif os.path.isdir(os.path.join(BASE, "inventario-mvc", "app")):
    PROJECT_DIR = os.path.join(BASE, "inventario-mvc")
else:
    for root, dirs, files in os.walk(BASE):
        if "app" in dirs and os.path.isfile(os.path.join(root, "app", "Models", "database.py")):
            PROJECT_DIR = root
            break
    else:
        PROJECT_DIR = BASE

sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)
print(f"[API] PROJECT_DIR = {PROJECT_DIR}")

from app.Models.database import Database
from app.Models.producto_model import ProductoModel
from app.Models.pedido_model import PedidoModel

app = Flask(__name__)
CORS(app)
Database.initialize()

# ── FRONTEND ───────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    for folder in [BASE, PROJECT_DIR]:
        if os.path.isfile(os.path.join(folder, "index.html")):
            return send_from_directory(folder, "index.html")
    return "<h1>index.html no encontrado</h1>", 404

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "project_dir": PROJECT_DIR})

# ── PRODUCTOS ──────────────────────────────────────────────────────────────

@app.route("/api/productos", methods=["GET"])
def listar_productos():
    termino = request.args.get("q", "").strip()
    try:
        rows = ProductoModel.buscar(termino) if termino else ProductoModel.obtener_todos(solo_activos=True)
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/productos/<int:pid>", methods=["GET"])
def detalle_producto(pid):
    try:
        row = ProductoModel.obtener_por_id(pid)
        if not row:
            return jsonify({"error": "No encontrado"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── CLIENTES ───────────────────────────────────────────────────────────────

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    try:
        return jsonify([dict(r) for r in PedidoModel.obtener_clientes()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clientes", methods=["POST"])
def crear_cliente():
    data = request.get_json(force=True)
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400
    try:
        cid = PedidoModel.crear_cliente(
            nombre,
            data.get("documento",""),
            data.get("telefono",""),
            data.get("email",""),
            data.get("direccion",""),
        )
        return jsonify({"id": cid, "nombre": nombre}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── PEDIDOS ────────────────────────────────────────────────────────────────

@app.route("/api/pedidos", methods=["POST"])
def crear_pedido():
    data       = request.get_json(force=True)
    cliente_id = data.get("cliente_id")
    items      = data.get("items", [])
    descuento  = float(data.get("descuento", 0))
    notas      = data.get("notas", "")

    if not cliente_id:
        return jsonify({"error": "cliente_id es requerido"}), 400
    if not items:
        return jsonify({"error": "El pedido debe tener al menos un ítem"}), 400

    for item in items:
        prod = ProductoModel.obtener_por_id(item["producto_id"])
        if not prod:
            return jsonify({"error": f"Producto {item['producto_id']} no existe"}), 400
        if prod["stock"] < item["cantidad"]:
            return jsonify({"error": f"Stock insuficiente para '{prod['nombre']}'. Disponible: {prod['stock']}"}), 400

    try:
        numero_factura = PedidoModel.crear_pedido(
            cliente_id=cliente_id, items=items,
            descuento=descuento, notas=notas, estado="pendiente",
        )
        pedido, items_det = PedidoModel.obtener_por_numero(numero_factura)
        return jsonify({
            "numero_factura": numero_factura,
            "pedido": dict(pedido) if pedido else {},
            "items":  [dict(i) for i in items_det],
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    try:
        return jsonify([dict(r) for r in PedidoModel.obtener_todos(limite=100)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos/<string:num>", methods=["GET"])
def detalle_pedido(num):
    try:
        pedido, items = PedidoModel.obtener_por_numero(num)
        if not pedido:
            return jsonify({"error": "Factura no encontrada"}), 404
        return jsonify({"pedido": dict(pedido), "items": [dict(i) for i in items]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos/<int:pid>/estado", methods=["PATCH"])
def actualizar_estado(pid):
    data   = request.get_json(force=True)
    estado = data.get("estado", "").strip()
    if estado not in {"pendiente","despachado","cancelado"}:
        return jsonify({"error": "Estado inválido"}), 400
    try:
        PedidoModel.actualizar_estado(pid, estado)
        return jsonify({"ok": True, "estado": estado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)