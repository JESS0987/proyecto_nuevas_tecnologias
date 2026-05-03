"""
Controller: Pedido
Ahora delega todas las operaciones a la API de Railway (api_client.py).
"""

import datetime
import api_client as api


class PedidoController:

    @staticmethod
    def listar_pedidos():
        return api.listar_pedidos()

    @staticmethod
    def obtener_pedido(pedido_id: int):
        return api.obtener_pedido_por_id(pedido_id)

    @staticmethod
    def listar_clientes():
        return api.listar_clientes()

    @staticmethod
    def crear_cliente(nombre, documento="", telefono="", email="", direccion=""):
        return api.crear_cliente(nombre, documento, telefono, email, direccion)

    @staticmethod
    def crear_pedido(cliente_id, items, descuento=0, notas="", estado="pendiente"):
        """
        items: lista de dicts con keys:
            producto_id, codigo, nombre, cantidad, precio_unitario
        """
        from app.Models.producto_model import ProductoModel

        # Enriquecer items con costo_unitario (viene del producto)
        items_api = []
        for item in items:
            prod = api.obtener_producto(item["producto_id"])
            items_api.append({
                "producto_id":     item["producto_id"],
                "cantidad":        item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "costo_unitario":  prod.get("costo", 0) if prod else 0,
            })

        return api.crear_pedido(
            cliente_id=cliente_id,
            items=items_api,
            descuento=descuento,
            notas=notas,
            estado=estado,
        )

    @staticmethod
    def cambiar_estado(pedido_id: int, nuevo_estado: str):
        estados_validos = {"pendiente", "despachado", "cancelado"}
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        api.actualizar_estado(pedido_id, nuevo_estado)

    @staticmethod
    def generar_texto_factura(numero_factura: str) -> str:
        pedido, items = api.obtener_pedido_por_numero(numero_factura)
        if not pedido:
            return "Factura no encontrada."

        lineas = [
            "=" * 48,
            "        ✦ GLAMOUR BISUTERÍA",
            "     Bucaramanga, Santander · Colombia",
            "=" * 48,
            f"  Factura : {pedido.get('numero_factura', numero_factura)}",
            f"  Fecha   : {str(pedido.get('fecha', ''))[:16]}",
            f"  Cliente : {pedido.get('cliente_nombre', '—')}",
            f"  Estado  : {pedido.get('estado', '—').upper()}",
            "-" * 48,
            f"  {'Producto':<22} {'Cant':>4} {'P.Unit':>9} {'Sub':>9}",
            "-" * 48,
        ]

        for i in items:
            nombre = str(i.get("producto_nombre") or i.get("nombre") or "")[:22]
            cant   = i.get("cantidad", 0)
            precio = i.get("precio_unitario", 0)
            sub    = i.get("subtotal", cant * precio)
            lineas.append(f"  {nombre:<22} {cant:>4} {precio:>9,.0f} {sub:>9,.0f}")

        subtotal  = pedido.get("subtotal", 0) or 0
        descuento = pedido.get("descuento", 0) or 0
        total     = pedido.get("total", subtotal - descuento)

        lineas += [
            "-" * 48,
            f"  {'Subtotal':>36} {subtotal:>9,.0f}",
        ]
        if descuento:
            lineas.append(f"  {'Descuento':>36} {descuento:>9,.0f}")
        lineas += [
            f"  {'TOTAL':>36} {total:>9,.0f}",
            "=" * 48,
            "  ¡Gracias por tu compra!",
            "  Jesús · Marlón · Sebastián — Grupo 3",
            "=" * 48,
        ]
        return "\n".join(lineas)