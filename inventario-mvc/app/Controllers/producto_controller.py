"""
Controller: Producto
Ahora delega todas las operaciones a la API de Railway (api_client.py).
"""

import api_client as api


class ProductoController:

    @staticmethod
    def listar_productos():
        return api.listar_productos()

    @staticmethod
    def buscar_productos(termino: str):
        return api.buscar_productos(termino)

    @staticmethod
    def obtener_producto(producto_id: int):
        return api.obtener_producto(producto_id)

    @staticmethod
    def productos_stock_bajo():
        productos = api.listar_productos()
        return [p for p in productos if p["stock"] <= p.get("stock_minimo", 5)]

    @staticmethod
    def listar_categorias():
        """
        Las categorías no tienen endpoint propio en la API.
        Las extraemos de los productos existentes.
        """
        productos  = api.listar_productos()
        vistas     = set()
        categorias = []
        for p in productos:
            nombre = p.get("categoria_nombre") or "General"
            cid    = p.get("categoria_id")
            if nombre not in vistas:
                vistas.add(nombre)
                categorias.append({"id": cid, "nombre": nombre})
        return sorted(categorias, key=lambda c: c["nombre"])

    @staticmethod
    def crear_producto(datos: dict):
        raise NotImplementedError(
            "La creación de productos debe hacerse desde la app de escritorio "
            "con acceso directo a la base de datos, o agregar el endpoint POST /api/productos."
        )

    @staticmethod
    def actualizar_producto(producto_id: int, datos: dict):
        raise NotImplementedError(
            "La actualización de productos debe hacerse desde la app de escritorio "
            "con acceso directo a la base de datos, o agregar el endpoint PUT /api/productos/<id>."
        )

    @staticmethod
    def eliminar_producto(producto_id: int):
        raise NotImplementedError(
            "La eliminación de productos debe hacerse desde la app de escritorio "
            "con acceso directo a la base de datos, o agregar el endpoint DELETE /api/productos/<id>."
        )

    @staticmethod
    def registrar_entrada(producto_id: int, cantidad: int,
                          costo_unitario: float, proveedor="", notas=""):
        raise NotImplementedError(
            "El registro de entradas debe hacerse desde la app de escritorio "
            "con acceso directo a la base de datos, o agregar el endpoint POST /api/entradas."
        )