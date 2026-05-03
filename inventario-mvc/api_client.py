"""
Cliente HTTP para la API de Railway.
Reemplaza las llamadas directas a SQLite local.
Todos los datos vienen de: https://inventarionuevastec.up.railway.app
"""

import requests

BASE_URL = "https://inventarionuevastec.up.railway.app"
TIMEOUT  = 10  # segundos


def _get(endpoint, params=None):
    r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(endpoint, data: dict):
    r = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _patch(endpoint, data: dict):
    r = requests.patch(f"{BASE_URL}{endpoint}", json=data, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ── Productos ──────────────────────────────────────────────────────────────

def listar_productos(solo_activos=True):
    """Retorna lista de dicts con todos los productos activos."""
    return _get("/api/productos")


def buscar_productos(termino: str):
    return _get("/api/productos", params={"q": termino})


def obtener_producto(producto_id: int):
    return _get(f"/api/productos/{producto_id}")


# ── Pedidos ────────────────────────────────────────────────────────────────

def listar_pedidos(limite=200):
    return _get("/api/pedidos")


def obtener_pedido_por_id(pedido_id: int):
    """Busca el pedido en la lista y retorna (pedido, items)."""
    pedidos = listar_pedidos()
    pedido  = next((p for p in pedidos if p["id"] == pedido_id), None)
    if not pedido:
        return None, []
    # Buscar por numero_factura para obtener items
    return obtener_pedido_por_numero(pedido["numero_factura"])


def obtener_pedido_por_numero(numero_factura: str):
    data = _get(f"/api/pedidos/{numero_factura}")
    return data.get("pedido", {}), data.get("items", [])


def crear_pedido(cliente_id, items, descuento=0, notas="", estado="pendiente"):
    """
    items: lista de dicts con keys:
        producto_id, cantidad, precio_unitario, costo_unitario
    Retorna numero_factura.
    """
    data = _post("/api/pedidos", {
        "cliente_id": cliente_id,
        "items":      items,
        "descuento":  descuento,
        "notas":      notas,
        "estado":     estado,
    })
    return data["numero_factura"]


def actualizar_estado(pedido_id: int, nuevo_estado: str):
    _patch(f"/api/pedidos/{pedido_id}/estado", {"estado": nuevo_estado})


# ── Clientes ───────────────────────────────────────────────────────────────

def listar_clientes():
    return _get("/api/clientes")


def crear_cliente(nombre, documento="", telefono="", email="", direccion=""):
    data = _post("/api/clientes", {
        "nombre":    nombre,
        "documento": documento,
        "telefono":  telefono,
        "email":     email,
        "direccion": direccion,
    })
    return data["id"]