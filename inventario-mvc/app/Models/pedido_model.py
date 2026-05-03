"""
Model: Pedido / Venta
Lógica de datos para ventas y facturación.
Escribe en SQLite Y sincroniza a MongoDB automáticamente.
"""

import datetime
from app.Models.database import (
    Database, mongo_upsert_pedido,
    _pedido_a_doc, _ts
)
from app.Models.producto_model import ProductoModel


class PedidoModel:

    # ------------------------------------------------------------------ #
    #  Generación de número de factura                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generar_numero_factura():
        anio = datetime.date.today().strftime("%Y")
        with Database.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM pedidos"
            ).fetchone()
            consecutivo = (row["cnt"] or 0) + 1
        return f"FAC-{anio}-{consecutivo:04d}"

    # ------------------------------------------------------------------ #
    #  Crear pedido — escribe SQLite + sincroniza Mongo                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def crear_pedido(cliente_id, items, descuento=0, notas="", estado="pendiente"):
        """
        items: lista de dicts con keys:
            producto_id, cantidad, precio_unitario, costo_unitario
        Retorna: numero_factura o lanza excepción.
        """
        if not items:
            raise ValueError("El pedido debe tener al menos un ítem.")

        numero_factura = PedidoModel._generar_numero_factura()
        subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
        total    = subtotal - descuento

        with Database.get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO pedidos
                   (numero_factura, cliente_id, subtotal, descuento, total, estado, notas)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (numero_factura, cliente_id, subtotal, descuento, total, estado, notas),
            )
            pedido_id = cur.lastrowid

            for item in items:
                sub = item["cantidad"] * item["precio_unitario"]
                conn.execute(
                    """INSERT INTO items_pedido
                       (pedido_id, producto_id, cantidad,
                        precio_unitario, costo_unitario, subtotal)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pedido_id, item["producto_id"], item["cantidad"],
                     item["precio_unitario"], item["costo_unitario"], sub),
                )
                ProductoModel.actualizar_stock(
                    item["producto_id"], -item["cantidad"], conn=conn
                )

            conn.commit()

        # ── Sincronizar a MongoDB ──────────────────────────────────────
        PedidoModel._sync_mongo(numero_factura)

        return numero_factura

    # ------------------------------------------------------------------ #
    #  Actualizar estado — escribe SQLite + sincroniza Mongo              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def actualizar_estado(pedido_id, nuevo_estado):
        with Database.get_connection() as conn:
            conn.execute(
                "UPDATE pedidos SET estado = ? WHERE id = ?",
                (nuevo_estado, pedido_id),
            )
            conn.commit()

        # ── Sincronizar a MongoDB ──────────────────────────────────────
        with Database.get_connection() as conn:
            row = conn.execute(
                "SELECT numero_factura FROM pedidos WHERE id = ?", (pedido_id,)
            ).fetchone()
        if row:
            PedidoModel._sync_mongo(row["numero_factura"])

    # ------------------------------------------------------------------ #
    #  Helper: leer pedido completo y enviarlo a Mongo                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sync_mongo(numero_factura):
        """Lee el pedido completo de SQLite y lo upserta en MongoDB."""
        try:
            pedido, items = PedidoModel.obtener_por_numero(numero_factura)
            if pedido:
                doc = _pedido_a_doc(dict(pedido), [dict(i) for i in items])
                mongo_upsert_pedido(doc)
        except Exception as e:
            print(f"[Mongo] sync pedido {numero_factura} error: {e}")

    # ------------------------------------------------------------------ #
    #  Consultas (solo SQLite — fuente de verdad)                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def obtener_todos(limite=200):
        sql = """
            SELECT p.*, c.nombre AS cliente_nombre
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.fecha DESC
            LIMIT ?
        """
        with Database.get_connection() as conn:
            return conn.execute(sql, (limite,)).fetchall()

    @staticmethod
    def obtener_por_numero(numero_factura):
        with Database.get_connection() as conn:
            pedido = conn.execute(
                """SELECT p.*, c.nombre AS cliente_nombre, c.documento
                   FROM pedidos p
                   LEFT JOIN clientes c ON p.cliente_id = c.id
                   WHERE p.numero_factura = ?""",
                (numero_factura,),
            ).fetchone()
            if not pedido:
                return None, []
            items = conn.execute(
                """SELECT ip.*, pr.nombre AS producto_nombre, pr.codigo
                   FROM items_pedido ip
                   JOIN productos pr ON ip.producto_id = pr.id
                   WHERE ip.pedido_id = ?""",
                (pedido["id"],),
            ).fetchall()
        return pedido, items

    @staticmethod
    def obtener_por_id(pedido_id):
        with Database.get_connection() as conn:
            pedido = conn.execute(
                """SELECT p.*, c.nombre AS cliente_nombre
                   FROM pedidos p
                   LEFT JOIN clientes c ON p.cliente_id = c.id
                   WHERE p.id = ?""",
                (pedido_id,),
            ).fetchone()
            items = conn.execute(
                """SELECT ip.*, pr.nombre AS producto_nombre, pr.codigo
                   FROM items_pedido ip
                   JOIN productos pr ON ip.producto_id = pr.id
                   WHERE ip.pedido_id = ?""",
                (pedido_id,),
            ).fetchall()
        return pedido, items

    # ------------------------------------------------------------------ #
    #  Clientes                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def obtener_clientes():
        with Database.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM clientes ORDER BY nombre"
            ).fetchall()

    @staticmethod
    def crear_cliente(nombre, documento="", telefono="", email="", direccion=""):
        documento = documento.strip() or None
        telefono  = telefono.strip()  or None
        email     = email.strip()     or None
        direccion = direccion.strip() or None
        with Database.get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO clientes (nombre, documento, telefono, email, direccion)
                   VALUES (?, ?, ?, ?, ?)""",
                (nombre, documento, telefono, email, direccion),
            )
            conn.commit()
            return cur.lastrowid