"""
Pruebas Unitarias — ProductoModel
Framework: pytest
Ejecutar: pytest tests/test_producto_model.py -v

Valida el núcleo del negocio de forma aislada usando una BD SQLite en memoria.
"""

import sys, os, pytest

# Asegurar que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "inventario-mvc"))

# Usar BD en memoria para no afectar datos reales
os.environ["DB_PATH"] = ":memory:"

from app.Models.database import Database
from app.Models.producto_model import ProductoModel


# ──────────────────────────────────────────────────────────────────────────
#  Fixture: inicializa una BD limpia antes de cada prueba
# ──────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def bd_limpia():
    """Crea tablas e inserta una categoría base antes de cada test."""
    Database.initialize()
    with Database.get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO categorias (id, nombre) VALUES (1, 'Bisutería')"
        )
        conn.commit()
    yield
    # Limpiar productos entre pruebas
    with Database.get_connection() as conn:
        conn.execute("DELETE FROM productos")
        conn.commit()


# ──────────────────────────────────────────────────────────────────────────
#  Pruebas Unitarias — CRUD Productos
# ──────────────────────────────────────────────────────────────────────────

class TestCrearProducto:

    def test_crear_producto_exitoso(self):
        """Camino feliz: crear un producto con datos válidos."""
        pid = ProductoModel.crear(
            codigo="P001", nombre="Aretes Dorados",
            descripcion="Aretes chapados en oro",
            categoria_id=1, costo=5000,
            precio_venta=10000, stock=20, stock_minimo=5
        )
        assert pid is not None
        assert pid > 0

    def test_producto_creado_se_puede_recuperar(self):
        """El producto creado debe poder obtenerse por su ID."""
        pid = ProductoModel.crear(
            codigo="P002", nombre="Collar Plata",
            descripcion="Collar de plata 925",
            categoria_id=1, costo=8000,
            precio_venta=15000, stock=10, stock_minimo=3
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto is not None
        assert producto["nombre"] == "Collar Plata"
        assert producto["codigo"] == "P002"
        assert producto["costo"] == 8000
        assert producto["precio_venta"] == 15000

    def test_crear_producto_codigo_unico(self):
        """No se puede crear dos productos con el mismo código."""
        ProductoModel.crear(
            codigo="P003", nombre="Pulsera",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=6000, stock=15, stock_minimo=2
        )
        with pytest.raises(Exception):
            ProductoModel.crear(
                codigo="P003", nombre="Pulsera Copia",
                descripcion="", categoria_id=1,
                costo=3000, precio_venta=6000, stock=5, stock_minimo=2
            )

    def test_listar_productos_activos(self):
        """Solo se listan productos activos."""
        ProductoModel.crear(
            codigo="P004", nombre="Dije Corazón",
            descripcion="", categoria_id=1,
            costo=2000, precio_venta=5000, stock=30, stock_minimo=5
        )
        productos = ProductoModel.obtener_todos(solo_activos=True)
        assert len(productos) >= 1
        nombres = [p["nombre"] for p in productos]
        assert "Dije Corazón" in nombres


class TestActualizarProducto:

    def test_actualizar_precio_exitoso(self):
        """El precio de venta debe actualizarse correctamente."""
        pid = ProductoModel.crear(
            codigo="P005", nombre="Anillo Ajustable",
            descripcion="", categoria_id=1,
            costo=4000, precio_venta=8000, stock=25, stock_minimo=5
        )
        ProductoModel.actualizar(
            pid, "P005", "Anillo Ajustable", "",
            1, 4000, 9500, 25, 5
        )
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["precio_venta"] == 9500

    def test_actualizar_stock_entrada(self):
        """Registrar una entrada debe incrementar el stock."""
        pid = ProductoModel.crear(
            codigo="P006", nombre="Tobillera",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=7000, stock=10, stock_minimo=3
        )
        ProductoModel.registrar_entrada(pid, cantidad=15, costo_unitario=3000)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto["stock"] == 25  # 10 + 15

    def test_actualizar_stock_negativo(self):
        """Reducir stock (salida de inventario) debe reflejarse."""
        pid = ProductoModel.crear(
            codigo="P007", nombre="Choker Terciopelo",
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
            codigo="P008", nombre="Set Bisutería",
            descripcion="", categoria_id=1,
            costo=12000, precio_venta=25000, stock=8, stock_minimo=2
        )
        ProductoModel.eliminar(pid)
        # No debe aparecer en la lista de activos
        activos = ProductoModel.obtener_todos(solo_activos=True)
        ids_activos = [p["id"] for p in activos]
        assert pid not in ids_activos
        # Pero sí debe poder obtenerse por ID (no fue borrado físicamente)
        producto = ProductoModel.obtener_por_id(pid)
        assert producto is not None


class TestBuscarProducto:

    def test_buscar_por_nombre(self):
        """La búsqueda por nombre debe retornar resultados relevantes."""
        ProductoModel.crear(
            codigo="P009", nombre="Aretes Gota Resina",
            descripcion="", categoria_id=1,
            costo=4000, precio_venta=7000, stock=20, stock_minimo=4
        )
        resultados = ProductoModel.buscar("gota")
        assert len(resultados) >= 1
        assert any("Gota" in p["nombre"] for p in resultados)

    def test_buscar_termino_inexistente(self):
        """Una búsqueda sin coincidencias debe retornar lista vacía."""
        resultados = ProductoModel.buscar("xyzproductoquenoexiste123")
        assert len(resultados) == 0

    def test_buscar_por_codigo(self):
        """La búsqueda también debe funcionar por código."""
        ProductoModel.crear(
            codigo="PTEST", nombre="Producto Test",
            descripcion="", categoria_id=1,
            costo=1000, precio_venta=2000, stock=5, stock_minimo=1
        )
        resultados = ProductoModel.buscar("PTEST")
        assert len(resultados) >= 1

    def test_obtener_por_codigo(self):
        """Debe poder recuperarse un producto activo por su código."""
        ProductoModel.crear(
            codigo="P010", nombre="Cadena Fina",
            descripcion="", categoria_id=1,
            costo=6000, precio_venta=12000, stock=15, stock_minimo=3
        )
        producto = ProductoModel.obtener_por_codigo("P010")
        assert producto is not None
        assert producto["nombre"] == "Cadena Fina"


class TestStockBajo:

    def test_detectar_stock_bajo(self):
        """Debe identificar productos cuyo stock es menor o igual al mínimo."""
        ProductoModel.crear(
            codigo="P011", nombre="Aretes Plateados",
            descripcion="", categoria_id=1,
            costo=3000, precio_venta=8000, stock=2, stock_minimo=5
        )
        bajos = ProductoModel.con_stock_bajo()
        nombres = [p["nombre"] for p in bajos]
        assert "Aretes Plateados" in nombres

    def test_stock_normal_no_aparece_en_bajos(self):
        """Un producto con stock suficiente no debe aparecer como bajo."""
        ProductoModel.crear(
            codigo="P012", nombre="Pulsera Perlas",
            descripcion="", categoria_id=1,
            costo=7000, precio_venta=14000, stock=50, stock_minimo=5
        )
        bajos = ProductoModel.con_stock_bajo()
        nombres = [p["nombre"] for p in bajos]
        assert "Pulsera Perlas" not in nombres
