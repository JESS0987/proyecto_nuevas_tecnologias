"""
Controller: Pedidos / Ventas
Lógica de negocio para el módulo de ventas y facturación.
"""

from app.Models.pedido_model import PedidoModel
from app.Models.producto_model import ProductoModel

ESTADOS_VALIDOS = ("pendiente", "despachado", "cancelado")


class PedidoController:

    # ------------------------------------------------------------------ #
    #  Crear pedido                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def crear_pedido(cliente_id, items_vista, descuento=0, notas="", estado="pendiente"):
        """
        items_vista: lista de dicts con:
            producto_id, cantidad, precio_unitario
        estado: estado inicial del pedido ('pendiente' por defecto)
        """
        if not items_vista:
            raise ValueError("Debe agregar al menos un producto al pedido.")

        if estado not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: '{estado}'. Use: {', '.join(ESTADOS_VALIDOS)}.")

        items_model = []
        for item in items_vista:
            producto = ProductoModel.obtener_por_id(item["producto_id"])
            if not producto:
                raise ValueError(f"Producto ID {item['producto_id']} no encontrado.")
            if producto["stock"] < item["cantidad"]:
                raise ValueError(
                    f"Stock insuficiente para '{producto['nombre']}'. "
                    f"Disponible: {producto['stock']}, solicitado: {item['cantidad']}."
                )
            items_model.append({
                "producto_id":     item["producto_id"],
                "cantidad":        item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "costo_unitario":  producto["costo"],
            })

        numero_factura = PedidoModel.crear_pedido(
            cliente_id, items_model, descuento, notas, estado
        )
        return numero_factura

    # ------------------------------------------------------------------ #
    #  Cambiar estado                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def cambiar_estado(pedido_id, nuevo_estado):
        """
        Cambia el estado de un pedido existente.
        nuevo_estado: 'pendiente' | 'despachado' | 'cancelado'
        """
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido: '{nuevo_estado}'. "
                f"Use: {', '.join(ESTADOS_VALIDOS)}."
            )
        PedidoModel.actualizar_estado(pedido_id, nuevo_estado)

    # ------------------------------------------------------------------ #
    #  Consultas                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def listar_pedidos(limite=200):
        return PedidoModel.obtener_todos(limite)

    @staticmethod
    def obtener_pedido(pedido_id):
        return PedidoModel.obtener_por_id(pedido_id)

    @staticmethod
    def obtener_pedido_por_factura(numero):
        return PedidoModel.obtener_por_numero(numero)

    # ------------------------------------------------------------------ #
    #  Clientes                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def listar_clientes():
        return PedidoModel.obtener_clientes()

    @staticmethod
    def crear_cliente(nombre, documento="", telefono="", email="", direccion=""):
        if not nombre.strip():
            raise ValueError("El nombre del cliente es obligatorio.")
        return PedidoModel.crear_cliente(
            nombre.strip(), documento, telefono, email, direccion
        )

    # ------------------------------------------------------------------ #
    #  Factura en texto                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def generar_texto_factura(numero_factura):
        pedido, items = PedidoModel.obtener_por_numero(numero_factura)
        if not pedido:
            return "Factura no encontrada."

        lineas = [
            "=" * 48,
            "       SISTEMA DE INVENTARIO Y RENTABILIDAD",
            "=" * 48,
            f"  Factura N°: {pedido['numero_factura']}",
            f"  Fecha:      {pedido['fecha']}",
            f"  Cliente:    {pedido['cliente_nombre'] or 'Consumidor Final'}",
            f"  Estado:     {pedido['estado'].capitalize()}",
            "-" * 48,
            f"  {'Producto':<22} {'Cant':>4} {'P.Unit':>8} {'Total':>8}",
            "-" * 48,
        ]
        for item in items:
            nombre = item["producto_nombre"][:22]
            lineas.append(
                f"  {nombre:<22} {item['cantidad']:>4} "
                f"{item['precio_unitario']:>8,.0f} "
                f"{item['subtotal']:>8,.0f}"
            )
        lineas += [
            "-" * 48,
            f"  {'Subtotal':>36}: {pedido['subtotal']:>8,.0f}",
            f"  {'Descuento':>36}: {pedido['descuento']:>8,.0f}",
            f"  {'TOTAL':>36}: {pedido['total']:>8,.0f}",
            "=" * 48,
            "       ¡Gracias por su compra!",
            "=" * 48,
        ]
        return "\n".join(lineas)