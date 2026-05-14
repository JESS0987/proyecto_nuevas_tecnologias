"""
API REST - Tienda de Bisutería · Glamour
SQLite para escritura + MongoDB para lectura persistente de pedidos
"""

import os, sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ── Detección automática de rutas ─────────────────────────────────────────
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

from app.Models.database import Database, get_mongo
from app.Models.producto_model import ProductoModel
from app.Models.pedido_model import PedidoModel

app = Flask(__name__)
CORS(app)
Database.initialize()

# ── HELPERS MONGO ──────────────────────────────────────────────────────────

def _serializar(doc):
    """Convierte un documento MongoDB a dict JSON-serializable."""
    if doc is None:
        return None
    d = dict(doc)
    # Convertir ObjectId y datetime a string
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
        elif str(type(v)) == "<class 'bson.objectid.ObjectId'>":
            d[k] = str(v)
        elif isinstance(v, dict):
            d[k] = _serializar(v)
        elif isinstance(v, list):
            d[k] = [_serializar(i) if isinstance(i, dict) else i for i in v]
    return d

def mongo_disponible():
    _, db = get_mongo()
    return db is not None

# ── FRONTEND ───────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    for folder in [BASE, PROJECT_DIR]:
        if os.path.isfile(os.path.join(folder, "index.html")):
            return send_from_directory(folder, "index.html")
    return "<h1>index.html no encontrado</h1>", 404

@app.route("/img/productos/<path:filename>", methods=["GET"])
def serve_imagen(filename):
    for folder in [BASE, PROJECT_DIR]:
        img_dir = os.path.join(folder, "img", "productos")
        if os.path.isdir(img_dir):
            return send_from_directory(img_dir, filename)
    return "Imagen no encontrada", 404

@app.route("/health", methods=["GET"])
def health():
    _, db = get_mongo()
    return jsonify({
        "status":       "ok",
        "project_dir":  PROJECT_DIR,
        "mongo":        db is not None,
        "mongo_db":     db.name if db else None,
    })

# ── PRODUCTOS ──────────────────────────────────────────────────────────────

@app.route("/api/productos", methods=["GET"])
def listar_productos():
    termino = request.args.get("q", "").strip()
    try:
        # Productos siempre desde SQLite (datos estáticos del catálogo)
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
        # Clientes: preferir Mongo si está disponible
        _, db = get_mongo()
        if db is not None:
            docs = list(db.clientes.find({}, {"_id": 0}))
            if docs:
                return jsonify([_serializar(d) for d in docs])
        # Fallback SQLite
        return jsonify([dict(r) for r in PedidoModel.obtener_clientes()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clientes", methods=["POST"])
def crear_cliente():
    data   = request.get_json(force=True)
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400
    try:
        cid = PedidoModel.crear_cliente(
            nombre,
            data.get("documento", ""),
            data.get("telefono",  ""),
            data.get("email",     ""),
            data.get("direccion", ""),
        )
        # Sincronizar cliente a Mongo
        _, db = get_mongo()
        if db is not None:
            db.clientes.update_one(
                {"sqlite_id": cid},
                {"$set": {"sqlite_id": cid, "nombre": nombre,
                          "documento": data.get("documento",""),
                          "telefono":  data.get("telefono",""),
                          "email":     data.get("email",""),
                          "direccion": data.get("direccion","")}},
                upsert=True
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
        pedido_dict = dict(pedido) if pedido else {}

        # El pedido_model ya sincroniza a Mongo automáticamente
        # Solo necesitamos devolver la respuesta
        return jsonify({
            "numero_factura": numero_factura,
            "pedido":         pedido_dict,
            "items":          [dict(i) for i in items_det],
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    try:
        # ── Leer desde MongoDB si está disponible ──────────────────────────
        _, db = get_mongo()
        if db is not None:
            docs = list(db.pedidos.find({}, {"_id": 0}).sort("fecha", -1).limit(200))
            if docs:
                # Adaptar campos para que el frontend los entienda igual
                resultado = []
                for d in _serializar_lista(docs):
                    resultado.append({
                        "id":              d.get("_id_sqlite"),
                        "numero_factura":  d.get("numero_factura"),
                        "numero":          d.get("numero_factura"),
                        "cliente_id":      d.get("cliente", {}).get("id"),
                        "cliente_nombre":  d.get("cliente", {}).get("nombre"),
                        "subtotal":        d.get("financiero", {}).get("subtotal", 0),
                        "descuento":       d.get("financiero", {}).get("descuento", 0),
                        "total":           d.get("financiero", {}).get("total", 0),
                        "estado":          d.get("estado"),
                        "fecha":           d.get("fecha"),
                        "notas":           d.get("notas"),
                        "num_items":       d.get("num_items", 0),
                    })
                return jsonify(resultado)

        # ── Fallback SQLite ────────────────────────────────────────────────
        return jsonify([dict(r) for r in PedidoModel.obtener_todos(limite=200)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pedidos/<string:num>", methods=["GET"])
def detalle_pedido(num):
    try:
        # Buscar en Mongo primero
        _, db = get_mongo()
        if db is not None:
            doc = db.pedidos.find_one({"numero_factura": num}, {"_id": 0})
            if doc:
                doc = _serializar(doc)
                return jsonify({
                    "pedido": {
                        "numero_factura": doc.get("numero_factura"),
                        "cliente_nombre": doc.get("cliente", {}).get("nombre"),
                        "subtotal":       doc.get("financiero", {}).get("subtotal", 0),
                        "descuento":      doc.get("financiero", {}).get("descuento", 0),
                        "total":          doc.get("financiero", {}).get("total", 0),
                        "estado":         doc.get("estado"),
                        "fecha":          doc.get("fecha"),
                    },
                    "items": doc.get("items", [])
                })

        # Fallback SQLite
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
    numero = data.get("numero_factura", "")
    if estado not in {"pendiente", "despachado", "cancelado"}:
        return jsonify({"error": "Estado inválido"}), 400
    try:
        # Actualizar en SQLite (también sincroniza a Mongo via pedido_model)
        PedidoModel.actualizar_estado(pid, estado)

        # Si SQLite falló pero Mongo está disponible, actualizar directo en Mongo
        _, db = get_mongo()
        if db is not None and numero:
            from datetime import datetime, timezone
            db.pedidos.update_one(
                {"numero_factura": numero},
                {"$set": {"estado": estado, "ultima_actualizacion": datetime.now(timezone.utc)}}
            )
        return jsonify({"ok": True, "estado": estado})
    except Exception as e:
        # Intentar solo Mongo si SQLite falla
        _, db = get_mongo()
        if db is not None and numero:
            from datetime import datetime, timezone
            db.pedidos.update_one(
                {"numero_factura": numero},
                {"$set": {"estado": estado, "ultima_actualizacion": datetime.now(timezone.utc)}}
            )
            return jsonify({"ok": True, "estado": estado, "via": "mongo"})
        return jsonify({"error": str(e)}), 500


def _serializar_lista(docs):
    return [_serializar(d) for d in docs]


# ── MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
