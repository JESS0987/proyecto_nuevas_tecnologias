"""
Pruebas Funcionales — API REST (Flask)
Framework: pytest + cliente de prueba de Flask
Ejecutar: pytest tests/test_api_funcional.py -v

Verifica el comportamiento correcto de los endpoints (Controladores).
"""

import sys, os, pytest, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventario-mvc"))

os.environ["DB_PATH"] = ":memory:"

# Importar la app Flask
from api import app as flask_app
from app.Models.database import Database
from app.Models.producto_model import ProductoModel


# ──────────────────────────────────────────────────────────────────────────
#  Fixtures
# ──────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """Cliente de prueba Flask configurado para testing."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def bd_limpia():
    """BD limpia con categoría y producto base antes de cada test."""
    Database.initialize()
    with Database.get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO categorias (id, nombre) VALUES (1, 'Bisutería')"
        )
        conn.commit()
    # Insertar un producto de prueba
    try:
        ProductoModel.crear(
            codigo="PTEST01", nombre="Producto de Prueba",
            descripcion="Para pruebas funcionales",
            categoria_id=1, costo=5000,
            precio_venta=10000, stock=20, stock_minimo=3
        )
    except Exception:
        pass
    yield
    with Database.get_connection() as conn:
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'PTEST%'")
        conn.commit()


# ──────────────────────────────────────────────────────────────────────────
#  Pruebas Funcionales — Endpoint /api/productos
# ──────────────────────────────────────────────────────────────────────────

class TestEndpointProductos:

    def test_listar_productos_retorna_200(self, client):
        """GET /api/productos debe retornar HTTP 200."""
        resp = client.get("/api/productos")
        assert resp.status_code == 200

    def test_listar_productos_retorna_lista(self, client):
        """La respuesta debe ser una lista JSON."""
        resp = client.get("/api/productos")
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_listar_productos_contiene_campos_requeridos(self, client):
        """Cada producto debe tener los campos esperados por el frontend."""
        resp = client.get("/api/productos")
        data = json.loads(resp.data)
        if len(data) > 0:
            producto = data[0]
            campos_requeridos = ["id", "codigo", "nombre", "precio_venta", "stock"]
            for campo in campos_requeridos:
                assert campo in producto, f"Falta el campo: {campo}"

    def test_buscar_producto_por_nombre(self, client):
        """GET /api/productos?q=prueba debe filtrar por nombre."""
        resp = client.get("/api/productos?q=Prueba")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any("Prueba" in p["nombre"] for p in data)

    def test_buscar_termino_inexistente_retorna_lista_vacia(self, client):
        """Búsqueda sin resultados debe retornar lista vacía, no error."""
        resp = client.get("/api/productos?q=ProductoXYZ999NoExiste")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_detalle_producto_existente(self, client):
        """GET /api/productos/<id> debe retornar el producto correcto."""
        # Obtener el ID del producto de prueba
        resp = client.get("/api/productos?q=PTEST01")
        data = json.loads(resp.data)
        if len(data) > 0:
            pid = data[0]["id"]
            resp2 = client.get(f"/api/productos/{pid}")
            assert resp2.status_code == 200
            detalle = json.loads(resp2.data)
            assert detalle["codigo"] == "PTEST01"

    def test_detalle_producto_inexistente_retorna_404(self, client):
        """GET /api/productos/99999 debe retornar HTTP 404."""
        resp = client.get("/api/productos/99999")
        assert resp.status_code == 404


# ──────────────────────────────────────────────────────────────────────────
#  Pruebas Funcionales — Endpoint /api/clientes
# ──────────────────────────────────────────────────────────────────────────

class TestEndpointClientes:

    def test_listar_clientes_retorna_200(self, client):
        """GET /api/clientes debe retornar HTTP 200."""
        resp = client.get("/api/clientes")
        assert resp.status_code == 200

    def test_crear_cliente_exitoso(self, client):
        """POST /api/clientes con datos válidos debe retornar HTTP 201."""
        payload = {
            "nombre": "Ana García Test",
            "documento": "1234567890",
            "telefono": "3001234567",
            "email": "ana@test.com",
            "direccion": "Calle 10 #20-30"
        }
        resp = client.post(
            "/api/clientes",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "id" in data
        assert data["nombre"] == "Ana García Test"

    def test_crear_cliente_sin_nombre_retorna_400(self, client):
        """POST /api/clientes sin nombre debe retornar HTTP 400."""
        payload = {"documento": "999", "telefono": ""}
        resp = client.post(
            "/api/clientes",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 400


# ──────────────────────────────────────────────────────────────────────────
#  Pruebas Funcionales — Endpoint /api/pedidos
# ──────────────────────────────────────────────────────────────────────────

class TestEndpointPedidos:

    def _crear_cliente(self, client, nombre="Cliente Test Pedido"):
        """Helper: crea un cliente y retorna su ID."""
        resp = client.post(
            "/api/clientes",
            data=json.dumps({"nombre": nombre}),
            content_type="application/json"
        )
        return json.loads(resp.data)["id"]

    def _id_producto_prueba(self, client):
        """Helper: obtiene el ID del producto de prueba."""
        resp = client.get("/api/productos?q=PTEST01")
        data = json.loads(resp.data)
        return data[0]["id"] if data else None

    def test_crear_pedido_exitoso(self, client):
        """POST /api/pedidos con datos válidos debe retornar HTTP 201."""
        cliente_id = self._crear_cliente(client)
        prod_id    = self._id_producto_prueba(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")

        payload = {
            "cliente_id": cliente_id,
            "items": [{
                "producto_id":    prod_id,
                "cantidad":       2,
                "precio_unitario": 10000,
                "costo_unitario":  5000
            }],
            "descuento": 0,
            "notas": "Pedido de prueba automatizado"
        }
        resp = client.post(
            "/api/pedidos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "numero_factura" in data
        assert data["numero_factura"].startswith("FAC-")

    def test_pedido_descuenta_stock(self, client):
        """Crear un pedido debe reducir el stock del producto."""
        cliente_id = self._crear_cliente(client, "Cliente Stock Test")
        prod_id    = self._id_producto_prueba(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")

        # Stock antes
        resp_antes = client.get(f"/api/productos/{prod_id}")
        stock_antes = json.loads(resp_antes.data)["stock"]

        # Crear pedido con cantidad 3
        payload = {
            "cliente_id": cliente_id,
            "items": [{
                "producto_id": prod_id, "cantidad": 3,
                "precio_unitario": 10000, "costo_unitario": 5000
            }],
            "descuento": 0, "notas": ""
        }
        client.post(
            "/api/pedidos",
            data=json.dumps(payload),
            content_type="application/json"
        )

        # Stock después
        resp_despues = client.get(f"/api/productos/{prod_id}")
        stock_despues = json.loads(resp_despues.data)["stock"]
        assert stock_despues == stock_antes - 3

    def test_pedido_sin_cliente_retorna_400(self, client):
        """Pedido sin cliente_id debe ser rechazado con HTTP 400."""
        payload = {
            "items": [{"producto_id": 1, "cantidad": 1,
                       "precio_unitario": 10000, "costo_unitario": 5000}]
        }
        resp = client.post(
            "/api/pedidos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 400

    def test_pedido_sin_items_retorna_400(self, client):
        """Pedido sin ítems debe ser rechazado con HTTP 400."""
        cliente_id = self._crear_cliente(client, "Cliente Sin Items")
        payload = {"cliente_id": cliente_id, "items": []}
        resp = client.post(
            "/api/pedidos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 400

    def test_pedido_stock_insuficiente_retorna_400(self, client):
        """Pedido con cantidad mayor al stock debe ser rechazado."""
        cliente_id = self._crear_cliente(client, "Cliente Stock Insuf")
        prod_id    = self._id_producto_prueba(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")

        payload = {
            "cliente_id": cliente_id,
            "items": [{
                "producto_id": prod_id, "cantidad": 9999,
                "precio_unitario": 10000, "costo_unitario": 5000
            }],
            "descuento": 0, "notas": ""
        }
        resp = client.post(
            "/api/pedidos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert resp.status_code == 400

    def test_listar_pedidos_retorna_200(self, client):
        """GET /api/pedidos debe retornar HTTP 200."""
        resp = client.get("/api/pedidos")
        assert resp.status_code == 200


# ──────────────────────────────────────────────────────────────────────────
#  Pruebas Funcionales — Endpoints del sistema
# ──────────────────────────────────────────────────────────────────────────

class TestEndpointSistema:

    def test_health_check(self, client):
        """GET /health debe confirmar que el servidor está activo."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"

    def test_frontend_carga(self, client):
        """GET / debe retornar el index.html o un mensaje de no encontrado."""
        resp = client.get("/")
        assert resp.status_code in [200, 404]
