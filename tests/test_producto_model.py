"""
Pruebas Unitarias — ProductoModel
Framework: pytest
Ejecutar: python -m pytest tests/test_producto_model.py -v
"""

import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventario-mvc"))
os.environ["DB_PATH"] = ":memory:"

from app.Models.database import Database
from app.Models.producto_model import ProductoModel


@pytest.fixture(autouse=True)
def bd_limpia():
    Database.initialize()
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'UT_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'UT_%'")
        conn.execute("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (1, 'Bisutería')")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    yield
    with Database.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM items_pedido WHERE producto_id IN (SELECT id FROM productos WHERE codigo LIKE 'UT_%')")
        conn.execute("DELETE FROM productos WHERE codigo LIKE 'UT_%'")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()


class TestCrearProducto:

    def test_crear_producto_exitoso(self):
        """Camino feliz: crear un producto con datos válidos."""
        pid = ProductoModel.crear(
            codigo="UT_A01", nombre="Aretes Test Dorados",
            descripcion="Test", categoria_id=1,
            costo=5000, precio_venta=10000, stock=20, stock_minimo=5
        )
        assert pid is not None and pid > 0

    def test_producto_creado_se_puede_recuperar(self):
        """El producto creado debe poder obtenerse por su ID."""
        pid = ProductoModel.crear(
            codigo="UT_A02", nombre="Collar Test Plata",
            descripcion="Test", categoria_id=1,
            costo=8000, precio_venta=15000, stock=10, stock_minimo=3
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto is not None
        assert producto["nombre"] == "Collar Test Plata"
        assert producto["codigo"] == "UT_A02"
        assert producto["costo"] == 8000
        assert producto["precio_venta"] == 15000

    def test_crear_producto_codigo_unico(self):
        """No se puede crear dos productos con el mismo código."""
        ProductoModel.crear(
            codigo="UT_A03", nombre="Pulsera Test",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=6000, stock=15, stock_minimo=2
        )
        with pytest.raises(Exception):
            ProductoModel.crear(
                codigo="UT_A03", nombre="Pulsera Copia",
                descripcion="", categoria_id=1,
                costo=3000, precio_venta=6000, stock=5, stock_minimo=2
            )

    def test_listar_productos_activos(self):
        """Solo se listan productos activos."""
        ProductoModel.crear(
            codigo="UT_A04", nombre="Dije Test Corazón",
            descripcion="", categoria_id=1,
            costo=2000, precio_venta=5000, stock=30, stock_minimo=5
        )
        productos = ProductoModel.obtener_todos(solo_activos=True)
        nombres = [p["nombre"] for p in productos]
        assert "Dije Test Corazón" in nombres


class TestActualizarProducto:

    def test_actualizar_precio_exitoso(self):
        """El precio de venta debe actualizarse correctamente."""
        pid = ProductoModel.crear(
            codigo="UT_B01", nombre="Anillo Test Ajustable",
            descripcion="", categoria_id=1,
            costo=4000, precio_venta=8000, stock=25, stock_minimo=5
        )
        ProductoModel.actualizar(pid, "UT_B01", "Anillo Test Ajustable", "", 1, 4000, 9500, 25, 5)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["precio_venta"] == 9500

    def test_actualizar_stock_entrada(self):
        """Registrar una entrada debe incrementar el stock."""
        pid = ProductoModel.crear(
            codigo="UT_B02", nombre="Tobillera Test",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=7000, stock=10, stock_minimo=3
        )
        ProductoModel.registrar_entrada(pid, cantidad=15, costo_unitario=3000)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 25  # 10 + 15

    def test_actualizar_stock_negativo(self):
        """Reducir stock debe reflejarse correctamente."""
        pid = ProductoModel.crear(
            codigo="UT_B03", nombre="Choker Test Terciopelo",
            descripcion="", categoria_id=1,
            costo=5000, precio_venta=9500, stock=20, stock_minimo=3
        )
        ProductoModel.actualizar_stock(pid, -5)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 15  # 20 - 5


class TestEliminarProducto:

    def test_eliminacion_logica(self):
        """Eliminar un producto lo desactiva, no lo borra físicamente."""
        pid = ProductoModel.crear(
            codigo="UT_C01", nombre="Set Test Bisutería",
            descripcion="", categoria_id=1,
            costo=12000, precio_venta=25000, stock=8, stock_minimo=2
        )
        ProductoModel.eliminar(pid)
        activos = ProductoModel.obtener_todos(solo_activos=True)
        ids_activos = [p["id"] for p in activos]
        assert pid not in ids_activos
        producto = ProductoModel.obtener_por_id(pid)
        assert producto is not None


class TestBuscarProducto:

    def test_buscar_por_nombre(self):
        """La búsqueda por nombre debe retornar resultados relevantes."""
        ProductoModel.crear(
            codigo="UT_D01", nombre="Aretes Test Gota Resina",
            descripcion="", categoria_id=1,
            costo=4000, precio_venta=7000, stock=20, stock_minimo=4
        )
        resultados = ProductoModel.buscar("Test Gota")
        assert len(resultados) >= 1
        assert any("Gota" in p["nombre"] for p in resultados)

    def test_buscar_termino_inexistente(self):
        """Una búsqueda sin coincidencias debe retornar lista vacía."""
        resultados = ProductoModel.buscar("xyzproductoquenoexiste999abc")
        assert len(resultados) == 0

    def test_buscar_por_codigo(self):
        """La búsqueda también debe funcionar por código."""
        ProductoModel.crear(
            codigo="UT_D02", nombre="Producto Test Buscar",
            descripcion="", categoria_id=1,
            costo=1000, precio_venta=2000, stock=5, stock_minimo=1
        )
        resultados = ProductoModel.buscar("UT_D02")
        assert len(resultados) >= 1

    def test_obtener_por_codigo(self):
        """Debe poder recuperarse un producto activo por su código."""
        ProductoModel.crear(
            codigo="UT_D03", nombre="Cadena Test Fina",
            descripcion="", categoria_id=1,
            costo=6000, precio_venta=12000, stock=15, stock_minimo=3
        )
        producto = ProductoModel.obtener_por_codigo("UT_D03")
        assert producto is not None
        assert producto["nombre"] == "Cadena Test Fina"


class TestStockBajo:

    def test_detectar_stock_bajo(self):
        """Debe identificar productos cuyo stock es menor o igual al mínimo."""
        ProductoModel.crear(
            codigo="UT_E01", nombre="Aretes Test Plateados",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=8000, stock=2, stock_minimo=5
        )
        bajos = ProductoModel.con_stock_bajo()
        nombres = [p["nombre"] for p in bajos]
        assert "Aretes Test Plateados" in nombres

    def test_stock_normal_no_aparece_en_bajos(self):
        """Un producto con stock suficiente no debe aparecer como bajo."""
        ProductoModel.crear(
            codigo="UT_E02", nombre="Pulsera Test Perlas",
            descripcion="", categoria_id=1,
            costo=7000, precio_venta=14000, stock=50, stock_minimo=5
        )
        bajos = ProductoModel.con_stock_bajo()
        nombres = [p["nombre"] for p in bajos]
        assert "Pulsera Test Perlas" not in nombres
