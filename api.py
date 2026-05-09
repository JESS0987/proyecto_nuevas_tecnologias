"""
API REST - Tienda de Bisutería · Glamour
Con autenticación MongoDB Atlas para usuarios y login
"""

import os, sys, hashlib
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

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

# ── MongoDB Atlas ──────────────────────────────────────────────────────────
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://oscardejesus0461_db_user:perrolobo0@jesusproyect.mx6bdzn.mongodb.net/glamour_inventario?retryWrites=true&w=majority&appName=JesusProyect"
)

try:
    mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo.admin.command("ping")
    mdb = mongo["glamour_inventario"]
    usuarios_col = mdb["usuarios"]
    pedidos_mongo = mdb["pedidos_web"]
    print("[MongoDB] Conectado correctamente ✅")

    # Crear índice único en username
    usuarios_col.create_index("username", unique=True)

    # Insertar admins por defecto si no existen
    ADMINS = [
        {"username": "marlon",    "password": hashlib.sha256("marlon123".encode()).hexdigest(), "nombre": "Marlón Gélvez",      "rol": "admin", "email": "marlon@glamour.co",    "telefono": "3111111111"},
        {"username": "jesus",     "password": hashlib.sha256("jesus123".encode()).hexdigest(),  "nombre": "Jesús González",     "rol": "admin", "email": "jesus@glamour.co",     "telefono": "3122222222"},
        {"username": "sebastian", "password": hashlib.sha256("seba123".encode()).hexdigest(),   "nombre": "Sebastián Velandia", "rol": "admin", "email": "sebastian@glamour.co", "telefono": "3133333333"},
    ]
    for admin in ADMINS:
        if not usuarios_col.find_one({"username": admin["username"]}):
            usuarios_col.insert_one(admin)
            print(f"[MongoDB] Admin '{admin['username']}' creado")

    MONGO_OK = True
except Exception as e:
    print(f"[MongoDB] Error conectando: {e}")
    MONGO_OK = False

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def user_to_dict(u):
    return {
        "id":        str(u["_id"]),
        "username":  u.get("username",""),
        "nombre":    u.get("nombre",""),
        "rol":       u.get("rol","cliente"),
        "email":     u.get("email",""),
        "telefono":  u.get("telefono",""),
        "documento": u.get("documento",""),
        "direccion": u.get("direccion",""),
    }

# ── FRONTEND ───────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    for folder in [BASE, PROJECT_DIR]:
        if os.path.isfile(os.path.join(folder, "index.html")):
            return send_from_directory(folder, "index.html")
    return "<h1>index.html no encontrado</h1>", 404

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mongo": MONGO_OK, "project_dir": PROJECT_DIR})

# ── AUTH ───────────────────────────────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    if not MONGO_OK:
        return jsonify({"error": "Base de datos no disponible"}), 503
    data = request.get_json(force=True)
    username = data.get("username","").strip()
    password = data.get("password","")
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    user = usuarios_col.find_one({"username": username, "password": hash_pass(password)})
    if not user:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
    return jsonify({"ok": True, "user": user_to_dict(user)})

@app.route("/api/auth/register", methods=["POST"])
def register():
    if not MONGO_OK:
        return jsonify({"error": "Base de datos no disponible"}), 503
    data = request.get_json(force=True)
    nombre   = data.get("nombre","").strip()
    username = data.get("username","").strip()
    password = data.get("password","")
    if not nombre or not username or not password:
        return jsonify({"error": "Nombre, usuario y contraseña son obligatorios"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    if usuarios_col.find_one({"username": username}):
        return jsonify({"error": "Ese nombre de usuario ya existe"}), 409
    new_user = {
        "username":  username,
        "password":  hash_pass(password),
        "nombre":    nombre,
        "rol":       "cliente",
        "email":     data.get("email",""),
        "telefono":  data.get("telefono",""),
        "documento": data.get("documento",""),
        "direccion": data.get("direccion",""),
        "creado_en": datetime.utcnow().isoformat(),
    }
    result = usuarios_col.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    return jsonify({"ok": True, "user": user_to_dict(new_user)}), 201

@app.route("/api/auth/perfil", methods=["PATCH"])
def actualizar_perfil():
    if not MONGO_OK:
        return jsonify({"error": "Base de datos no disponible"}), 503
    data    = request.get_json(force=True)
    user_id = data.get("user_id","")
    if not user_id:
        return jsonify({"error": "user_id requerido"}), 400
    update = {}
    for field in ["nombre","email","telefono","documento","direccion"]:
        if field in data:
            update[field] = data[field]
    if not update:
        return jsonify({"error": "Nada que actualizar"}), 400
    usuarios_col.update_one({"_id": ObjectId(user_id)}, {"$set": update})
    user = usuarios_col.find_one({"_id": ObjectId(user_id)})
    return jsonify({"ok": True, "user": user_to_dict(user)})

# ── PEDIDOS WEB (MongoDB) ──────────────────────────────────────────────────
@app.route("/api/auth/mis-pedidos", methods=["GET"])
def mis_pedidos():
    if not MONGO_OK:
        return jsonify([])
    user_id = request.args.get("user_id","")
    if not user_id:
        return jsonify({"error": "user_id requerido"}), 400
    pedidos = list(pedidos_mongo.find({"user_id": user_id}).sort("fecha", -1).limit(50))
    for p in pedidos:
        p["_id"] = str(p["_id"])
    return jsonify(pedidos)

@app.route("/api/auth/mis-pedidos/<string:pid>/cancelar", methods=["PATCH"])
def cancelar_mi_pedido(pid):
    if not MONGO_OK:
        return jsonify({"error": "No disponible"}), 503
    pedidos_mongo.update_one(
        {"_id": ObjectId(pid), "estado": "pendiente"},
        {"$set": {"estado": "cancelado"}}
    )
    return jsonify({"ok": True})

# ── USUARIOS (admin) ───────────────────────────────────────────────────────
@app.route("/api/auth/usuarios", methods=["GET"])
def listar_usuarios():
    if not MONGO_OK:
        return jsonify([])
    users = list(usuarios_col.find({}))
    return jsonify([user_to_dict(u) for u in users])

# ── PRODUCTOS ──────────────────────────────────────────────────────────────
@app.route("/api/productos", methods=["GET"])
def listar_productos():
    termino = request.args.get("q","").strip()
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
    nombre = data.get("nombre","").strip()
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
    items      = data.get("items",[])
    descuento  = float(data.get("descuento",0))
    notas      = data.get("notas","")
    user_id    = data.get("user_id","")  # opcional, para guardar en MongoDB

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

        # Guardar en MongoDB si hay user_id
        if MONGO_OK and user_id:
            pedidos_mongo.insert_one({
                "user_id":        user_id,
                "numero":         numero_factura,
                "fecha":          datetime.utcnow().isoformat(),
                "estado":         "pendiente",
                "total":          float(pedido["total"]) if pedido else 0,
                "subtotal":       float(pedido["subtotal"]) if pedido else 0,
                "descuento":      descuento,
                "cliente_nombre": pedido["cliente_nombre"] if pedido else "",
                "items": [{"nombre": i["producto_nombre"], "cantidad": i["cantidad"],
                           "precio": float(i["precio_unitario"]), "subtotal": float(i["subtotal"])}
                          for i in items_det],
            })

        return jsonify({
            "numero_factura": numero_factura,
            "pedido":  dict(pedido) if pedido else {},
            "items":   [dict(i) for i in items_det],
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
    estado = data.get("estado","").strip()
    if estado not in {"pendiente","despachado","cancelado"}:
        return jsonify({"error": "Estado inválido"}), 400
    try:
        PedidoModel.actualizar_estado(pid, estado)
        # Sincronizar en MongoDB por número de factura
        if MONGO_OK:
            num = data.get("numero_factura","")
            if num:
                pedidos_mongo.update_many({"numero": num}, {"$set": {"estado": estado}})
        return jsonify({"ok": True, "estado": estado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
