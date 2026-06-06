"""
Pruebas Unitarias y Funcionales — Inventario / Entradas / Categorias
Autor: Marlon Gelvez (TechSoft Solutions S.A.S.)
Framework: pytest
Ejecutar: python -m pytest tests/test_inventario_marlon.py -v
"""

import sys, os, pytest, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventario-mvc"))
os.environ["DB_PATH"] = ":memory:"

from app.Models.database import Database
from app.Models.producto_model import ProductoModel


# ======================================================================
#  FIXTURE: base de datos limpia antes/despues de cada prueba
# ======================================================================

@pytest.fixture(autouse=True)
def bd_limpia():
    Database.initialize()
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM entradas_inventario WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'ML_%')")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'ML_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'ML_%'")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    yield
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM entradas_inventario WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'ML_%')")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'ML_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'ML_%'")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()


# ======================================================================
#  PRUEBAS UNITARIAS - Entradas de Inventario
# ======================================================================

class TestEntradasInventario:

    def test_registrar_entrada_incrementa_stock(self):
        """Registrar una entrada debe sumar correctamente la cantidad al stock actual."""
        pid = ProductoModel.crear(
            codigo="ML_ENT01", nombre="Aretes Marlon Dorados",
            descripcion="Aretes de prueba", categoria_id=2,
            costo=4000, precio_venta=9000, stock=10, stock_minimo=3
        )
        ProductoModel.registrar_entrada(pid, cantidad=20, costo_unitario=4000, proveedor="Proveedor Test")
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 30  # 10 + 20

    def test_registrar_entrada_actualiza_costo(self):
        """El costo unitario debe actualizarse con la nueva entrada."""
        pid = ProductoModel.crear(
            codigo="ML_ENT02", nombre="Collar Marlon Plateado",
            descripcion="Collar de prueba", categoria_id=2,
            costo=5000, precio_venta=12000, stock=5, stock_minimo=2
        )
        ProductoModel.registrar_entrada(pid, cantidad=10, costo_unitario=6500, proveedor="Dist. Nacional")
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["costo"] == 6500

    def test_historial_entradas_registra_movimiento(self):
        """Despues de una entrada, el historial debe contener al menos un registro."""
        pid = ProductoModel.crear(
            codigo="ML_ENT03", nombre="Pulsera Marlon Hilo",
            descripcion="Pulsera de prueba", categoria_id=2,
            costo=2500, precio_venta=5000, stock=8, stock_minimo=2
        )
        ProductoModel.registrar_entrada(pid, cantidad=12, costo_unitario=2500, notas="Reposicion mensual")
        historial = ProductoModel.historial_entradas(producto_id=pid)
        assert len(historial) >= 1

    def test_historial_entradas_contiene_cantidad_correcta(self):
        """El registro del historial debe reflejar exactamente la cantidad ingresada."""
        pid = ProductoModel.crear(
            codigo="ML_ENT04", nombre="Tobillera Marlon Tejida",
            descripcion="Tobillera de prueba", categoria_id=2,
            costo=3000, precio_venta=7000, stock=6, stock_minimo=2
        )
        ProductoModel.registrar_entrada(pid, cantidad=25, costo_unitario=3000)
        historial = ProductoModel.historial_entradas(producto_id=pid)
        assert historial[0]["cantidad"] == 25

    def test_multiples_entradas_acumulan_stock(self):
        """Varias entradas consecutivas deben acumular el stock total."""
        pid = ProductoModel.crear(
            codigo="ML_ENT05", nombre="Dije Marlon Estrella",
            descripcion="Dije de prueba", categoria_id=2,
            costo=1500, precio_venta=4000, stock=5, stock_minimo=3
        )
        ProductoModel.registrar_entrada(pid, cantidad=10, costo_unitario=1500)
        ProductoModel.registrar_entrada(pid, cantidad=15, costo_unitario=1500)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 30  # 5 + 10 + 15


# ======================================================================
#  PRUEBAS UNITARIAS - Categorias
# ======================================================================

class TestCategorias:

    def test_obtener_categorias_retorna_lista(self):
        """El sistema debe devolver al menos las categorias insertadas."""
        categorias = ProductoModel.obtener_categorias()
        assert isinstance(categorias, list)
        assert len(categorias) >= 1

    def test_categorias_contienen_campo_nombre(self):
        """Cada categoria debe tener el campo nombre."""
        categorias = ProductoModel.obtener_categorias()
        for cat in categorias:
            assert "nombre" in dict(cat)

    def test_producto_hereda_nombre_categoria(self):
        """El producto debe mostrar el nombre de su categoria correctamente."""
        pid = ProductoModel.crear(
            codigo="ML_CAT01", nombre="Aretes Marlon Resina",
            descripcion="Con categoria Bisuteria", categoria_id=2,
            costo=3000, precio_venta=7000, stock=15, stock_minimo=3
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["categoria_nombre"] == "Bisutería"

    def test_producto_categoria_general(self):
        """Un producto de categoria General debe reflejar ese nombre."""
        pid = ProductoModel.crear(
            codigo="ML_CAT02", nombre="Bolso Marlon Mini",
            descripcion="Accesorio de moda", categoria_id=1,
            costo=15000, precio_venta=30000, stock=5, stock_minimo=1
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["categoria_nombre"] == "General"


# ======================================================================
#  PRUEBAS UNITARIAS - Validaciones adicionales del modelo
# ======================================================================

class TestValidacionesModelo:

    def test_producto_inactivo_no_aparece_en_busqueda(self):
        """Un producto eliminado no debe aparecer en resultados de busqueda."""
        pid = ProductoModel.crear(
            codigo="ML_VAL01", nombre="Cadena Marlon Inactiva",
            descripcion="Producto para eliminar", categoria_id=2,
            costo=5000, precio_venta=10000, stock=10, stock_minimo=2
        )
        ProductoModel.eliminar(pid)
        resultados = ProductoModel.buscar("Cadena Marlon Inactiva")
        assert all(p["id"] != pid for p in resultados)

    def test_producto_inactivo_no_aparece_en_obtener_por_codigo(self):
        """Un producto eliminado no debe ser retornado por obtener_por_codigo."""
        pid = ProductoModel.crear(
            codigo="ML_VAL02", nombre="Anillo Marlon Inactivo",
            descripcion="Para verificar inactivacion", categoria_id=2,
            costo=4000, precio_venta=8000, stock=5, stock_minimo=1
        )
        ProductoModel.eliminar(pid)
        resultado = ProductoModel.obtener_por_codigo("ML_VAL02")
        assert resultado is None

    def test_actualizar_stock_con_cero_no_cambia_valor(self):
        """Ajustar stock en 0 no debe cambiar el stock actual."""
        pid = ProductoModel.crear(
            codigo="ML_VAL03", nombre="Choker Marlon Negro",
            descripcion="", categoria_id=2,
            costo=2000, precio_venta=5000, stock=12, stock_minimo=3
        )
        ProductoModel.actualizar_stock(pid, 0)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 12

    def test_actualizar_nombre_y_descripcion(self):
        """Actualizar nombre y descripcion debe persistir los cambios."""
        pid = ProductoModel.crear(
            codigo="ML_VAL04", nombre="Pulsera Marlon Original",
            descripcion="Descripcion original", categoria_id=2,
            costo=3500, precio_venta=7000, stock=10, stock_minimo=2
        )
        ProductoModel.actualizar(
            pid, "ML_VAL04", "Pulsera Marlon Actualizada",
            "Descripcion nueva", 2, 3500, 7000, 10, 2
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["nombre"] == "Pulsera Marlon Actualizada"
        assert producto["descripcion"] == "Descripcion nueva"

    def test_stock_bajo_con_stock_igual_a_minimo(self):
        """Un producto con stock exactamente igual al minimo debe aparecer como stock bajo."""
        pid = ProductoModel.crear(
            codigo="ML_VAL05", nombre="Set Marlon Exacto",
            descripcion="", categoria_id=2,
            costo=6000, precio_venta=13000, stock=5, stock_minimo=5
        )
        bajos = ProductoModel.con_stock_bajo()
        ids_bajos = [p["id"] for p in bajos]
        assert pid in ids_bajos


# ======================================================================
#  PRUEBAS FUNCIONALES - API REST
# ======================================================================

from api import app as flask_app


@pytest.fixture(scope="module")
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestEndpointEntradas:

    def _crear_producto_funcional(self):
        try:
            pid = ProductoModel.crear(
                codigo="ML_FT01", nombre="Producto Marlon Funcional",
                descripcion="Para pruebas funcionales",
                categoria_id=2, costo=4000,
                precio_venta=9000, stock=20, stock_minimo=3
            )
            return pid
        except Exception:
            row = ProductoModel.obtener_por_codigo("ML_FT01")
            return row["id"] if row else None

    def test_listar_productos_con_filtro_q_retorna_200(self, client):
        """El endpoint GET /api/productos?q=X debe responder 200."""
        resp = client.get("/api/productos?q=Marlon")
        assert resp.status_code == 200

    def test_respuesta_productos_es_json_valido(self, client):
        """La respuesta del listado de productos debe ser JSON parseable."""
        resp = client.get("/api/productos")
        assert resp.content_type == "application/json"
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_detalle_producto_retorna_campos_esperados(self, client):
        """El detalle de un producto existente debe incluir campos clave."""
        pid = self._crear_producto_funcional()
        if not pid:
            pytest.skip("No se pudo crear producto de prueba")
        resp = client.get(f"/api/productos/{pid}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        for campo in ["id", "codigo", "nombre", "precio_venta", "stock", "costo"]:
            assert campo in data, f"Falta el campo: {campo}"

    def test_crear_cliente_con_telefono_y_email(self, client):
        """Crear un cliente con todos los campos opcionales debe retornar 201."""
        import time
        payload = {
            "nombre": "Marlon Test Cliente",
            "documento": f"ML{int(time.time())}",
            "telefono": "3157894561",
            "email": "marlon@techsoft.co",
            "direccion": "Calle 45 # 12-34, Bucaramanga"
        }
        resp = client.post("/api/clientes",
                           data=json.dumps(payload),
                           content_type="application/json")
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["nombre"] == "Marlon Test Cliente"

    def test_crear_pedido_sin_producto_existente_retorna_400(self, client):
        """Un pedido con producto_id inexistente debe retornar 400."""
        resp_cli = client.post("/api/clientes",
                               data=json.dumps({"nombre": "Cliente ML Error"}),
                               content_type="application/json")
        cliente_id = json.loads(resp_cli.data)["id"]
        payload = {
            "cliente_id": cliente_id,
            "items": [{"producto_id": 999999, "cantidad": 1,
                       "precio_unitario": 10000, "costo_unitario": 5000}],
            "descuento": 0
        }
        resp = client.post("/api/pedidos",
                           data=json.dumps(payload),
                           content_type="application/json")
        assert resp.status_code == 400

    def test_health_retorna_status_ok(self, client):
        """El endpoint /health debe retornar status ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"

    def test_listar_pedidos_retorna_lista(self, client):
        """GET /api/pedidos debe retornar una lista."""
        resp = client.get("/api/pedidos")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
