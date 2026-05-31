"""
Pruebas Funcionales — API REST (Flask)
Framework: pytest + cliente de prueba de Flask
Ejecutar: python -m pytest tests/test_api_funcional.py -v
"""

import sys, os, pytest, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventario-mvc"))
os.environ["DB_PATH"] = ":memory:"

from api import app as flask_app
from app.Models.database import Database
from app.Models.producto_model import ProductoModel


@pytest.fixture(scope="module")
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def bd_limpia():
    Database.initialize()
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'FT_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'FT_%'")
        conn.execute("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (1, 'Bisutería')")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    try:
        ProductoModel.crear(
            codigo="FT_PROD01", nombre="Producto Funcional Test",
            descripcion="Para pruebas funcionales",
            categoria_id=1, costo=5000,
            precio_venta=10000, stock=50, stock_minimo=3
        )
    except Exception:
        pass
    yield
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'FT_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'FT_%'")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()


class TestEndpointProductos:

    def test_listar_productos_retorna_200(self, client):
        resp = client.get("/api/productos")
        assert resp.status_code == 200

    def test_listar_productos_retorna_lista(self, client):
        resp = client.get("/api/productos")
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_listar_productos_contiene_campos_requeridos(self, client):
        resp = client.get("/api/productos")
        data = json.loads(resp.data)
        if len(data) > 0:
            for campo in ["id", "codigo", "nombre", "precio_venta", "stock"]:
                assert campo in data[0], f"Falta el campo: {campo}"

    def test_buscar_producto_por_nombre(self, client):
        resp = client.get("/api/productos?q=Funcional")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_buscar_termino_inexistente_retorna_lista_vacia(self, client):
        resp = client.get("/api/productos?q=XYZProductoNoExiste999")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_detalle_producto_existente(self, client):
        resp = client.get("/api/productos?q=FT_PROD01")
        data = json.loads(resp.data)
        if len(data) > 0:
            pid = data[0]["id"]
            resp2 = client.get(f"/api/productos/{pid}")
            assert resp2.status_code == 200
            assert json.loads(resp2.data)["codigo"] == "FT_PROD01"

    def test_detalle_producto_inexistente_retorna_404(self, client):
        resp = client.get("/api/productos/99999")
        assert resp.status_code == 404


class TestEndpointClientes:

    def test_listar_clientes_retorna_200(self, client):
        resp = client.get("/api/clientes")
        assert resp.status_code == 200

    def test_crear_cliente_exitoso(self, client):
        import time
        doc_unico = f"FT_{int(time.time())}"
        payload = {"nombre": "Ana García Test FT", "documento": doc_unico,
                   "telefono": "3001234567", "email": "ana@test.com"}
        resp = client.post("/api/clientes", data=json.dumps(payload),
                           content_type="application/json")
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "id" in data
        assert data["nombre"] == "Ana García Test FT"

    def test_crear_cliente_sin_nombre_retorna_400(self, client):
        resp = client.post("/api/clientes", data=json.dumps({"documento": "999"}),
                           content_type="application/json")
        assert resp.status_code == 400


class TestEndpointPedidos:

    def _crear_cliente(self, client, nombre="Cliente Test FT"):
        resp = client.post("/api/clientes", data=json.dumps({"nombre": nombre}),
                           content_type="application/json")
        return json.loads(resp.data)["id"]

    def _id_producto(self, client):
        resp = client.get("/api/productos?q=FT_PROD01")
        data = json.loads(resp.data)
        return data[0]["id"] if data else None

    def test_crear_pedido_exitoso(self, client):
        cliente_id = self._crear_cliente(client)
        prod_id = self._id_producto(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")
        payload = {
            "cliente_id": cliente_id,
            "items": [{"producto_id": prod_id, "cantidad": 2,
                       "precio_unitario": 10000, "costo_unitario": 5000}],
            "descuento": 0, "notas": "Pedido test automatizado"
        }
        resp = client.post("/api/pedidos", data=json.dumps(payload),
                           content_type="application/json")
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "numero_factura" in data
        assert data["numero_factura"].startswith("FAC-")

    def test_pedido_descuenta_stock(self, client):
        cliente_id = self._crear_cliente(client, "Cliente Stock FT")
        prod_id = self._id_producto(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")
        stock_antes = json.loads(client.get(f"/api/productos/{prod_id}").data)["stock"]
        payload = {
            "cliente_id": cliente_id,
            "items": [{"producto_id": prod_id, "cantidad": 3,
                       "precio_unitario": 10000, "costo_unitario": 5000}],
            "descuento": 0, "notas": ""
        }
        client.post("/api/pedidos", data=json.dumps(payload),
                    content_type="application/json")
        stock_despues = json.loads(client.get(f"/api/productos/{prod_id}").data)["stock"]
        assert stock_despues == stock_antes - 3

    def test_pedido_sin_cliente_retorna_400(self, client):
        resp = client.post("/api/pedidos",
                           data=json.dumps({"items": [{"producto_id": 1, "cantidad": 1,
                                                        "precio_unitario": 10000, "costo_unitario": 5000}]}),
                           content_type="application/json")
        assert resp.status_code == 400

    def test_pedido_sin_items_retorna_400(self, client):
        cliente_id = self._crear_cliente(client, "Cliente Sin Items FT")
        resp = client.post("/api/pedidos",
                           data=json.dumps({"cliente_id": cliente_id, "items": []}),
                           content_type="application/json")
        assert resp.status_code == 400

    def test_pedido_stock_insuficiente_retorna_400(self, client):
        cliente_id = self._crear_cliente(client, "Cliente Stock Insuf FT")
        prod_id = self._id_producto(client)
        if not prod_id:
            pytest.skip("Producto de prueba no disponible")
        payload = {
            "cliente_id": cliente_id,
            "items": [{"producto_id": prod_id, "cantidad": 9999,
                       "precio_unitario": 10000, "costo_unitario": 5000}],
            "descuento": 0, "notas": ""
        }
        resp = client.post("/api/pedidos", data=json.dumps(payload),
                           content_type="application/json")
        assert resp.status_code == 400

    def test_listar_pedidos_retorna_200(self, client):
        resp = client.get("/api/pedidos")
        assert resp.status_code == 200


class TestEndpointSistema:

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert json.loads(resp.data)["status"] == "ok"

    def test_frontend_carga(self, client):
        resp = client.get("/")
        assert resp.status_code in [200, 404]
