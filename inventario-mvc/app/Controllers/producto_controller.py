"""
Controller: Productos
Lógica de negocio para el módulo de inventario.
"""

from app.Models.producto_model import ProductoModel
from config.settings import DEFAULT_STOCK_MINIMO


class ProductoController:

    # ------------------------------------------------------------------ #
    #  Listados                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def listar_productos(solo_activos=True):
        return ProductoModel.obtener_todos(solo_activos)

    @staticmethod
    def buscar_productos(termino):
        if not termino.strip():
            return ProductoModel.obtener_todos()
        return ProductoModel.buscar(termino.strip())

    @staticmethod
    def obtener_producto(producto_id):
        return ProductoModel.obtener_por_id(producto_id)

    @staticmethod
    def obtener_por_codigo(codigo):
        return ProductoModel.obtener_por_codigo(codigo)

    @staticmethod
    def listar_categorias():
        return ProductoModel.obtener_categorias()

    # ------------------------------------------------------------------ #
    #  Creación / edición                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def crear_producto(datos):
        """
        datos: dict con keys:
            codigo, nombre, descripcion, categoria_id,
            costo, precio_venta, stock, stock_minimo
        """
        errores = ProductoController._validar(datos)
        if errores:
            raise ValueError("\n".join(errores))

        return ProductoModel.crear(
            codigo       = datos["codigo"].strip().upper(),
            nombre       = datos["nombre"].strip(),
            descripcion  = datos.get("descripcion", "").strip(),
            categoria_id = datos.get("categoria_id"),
            costo        = float(datos["costo"]),
            precio_venta = float(datos["precio_venta"]),
            stock        = int(datos["stock"]),
            stock_minimo = int(datos.get("stock_minimo", DEFAULT_STOCK_MINIMO)),
        )

    @staticmethod
    def actualizar_producto(producto_id, datos):
        errores = ProductoController._validar(datos, producto_id)
        if errores:
            raise ValueError("\n".join(errores))

        ProductoModel.actualizar(
            producto_id  = producto_id,
            codigo       = datos["codigo"].strip().upper(),
            nombre       = datos["nombre"].strip(),
            descripcion  = datos.get("descripcion", "").strip(),
            categoria_id = datos.get("categoria_id"),
            costo        = float(datos["costo"]),
            precio_venta = float(datos["precio_venta"]),
            stock        = int(datos["stock"]),
            stock_minimo = int(datos.get("stock_minimo", DEFAULT_STOCK_MINIMO)),
        )

    @staticmethod
    def eliminar_producto(producto_id):
        ProductoModel.eliminar(producto_id)

    # ------------------------------------------------------------------ #
    #  Entradas de inventario                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def registrar_entrada(producto_id, cantidad, costo_unitario,
                          proveedor="", notas=""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        if costo_unitario < 0:
            raise ValueError("El costo no puede ser negativo.")
        ProductoModel.registrar_entrada(
            producto_id, cantidad, costo_unitario, proveedor, notas
        )

    @staticmethod
    def productos_stock_bajo():
        return ProductoModel.con_stock_bajo()

    # ------------------------------------------------------------------ #
    #  Validación                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validar(datos, producto_id=None):
        errores = []
        if not datos.get("codigo", "").strip():
            errores.append("El código es obligatorio.")
        if not datos.get("nombre", "").strip():
            errores.append("El nombre es obligatorio.")
        try:
            costo = float(datos.get("costo", -1))
            if costo < 0:
                raise ValueError
        except (ValueError, TypeError):
            errores.append("El costo debe ser un número positivo.")
        try:
            pventa = float(datos.get("precio_venta", -1))
            if pventa < 0:
                raise ValueError
        except (ValueError, TypeError):
            errores.append("El precio de venta debe ser un número positivo.")
        try:
            stock = int(datos.get("stock", -1))
            if stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            errores.append("El stock debe ser un número entero positivo.")

        # Verificar código duplicado
        if not errores and datos.get("codigo"):
            existente = ProductoModel.obtener_por_codigo(
                datos["codigo"].strip().upper()
            )
            if existente and existente["id"] != producto_id:
                errores.append(
                    f"Ya existe un producto con el código "
                    f"'{datos['codigo'].upper()}'."
                )
        return errores
