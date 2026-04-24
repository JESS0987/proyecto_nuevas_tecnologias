"""
Model: Pedido / Venta
Lógica de datos para ventas y facturación.
"""

import datetime
from app.Models.database import Database
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
    #  Crear pedido (transacción completa)                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def crear_pedido(cliente_id, items, descuento=0, notas="", estado="pendiente"):
        """
        items: lista de dicts con keys:
            producto_id, cantidad, precio_unitario, costo_unitario
        estado: estado inicial ('pendiente' por defecto)
        Retorna: numero_factura o lanza excepción.
        """
        if not items:
            raise ValueError("El pedido debe tener al menos un ítem.")

        numero_factura = PedidoModel._generar_numero_factura()
        subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
        total    = subtotal - descuento

        with Database.get_connection() as conn:
            # Insertar cabecera del pedido
            cur = conn.execute(
                """INSERT INTO pedidos
                   (numero_factura, cliente_id, subtotal, descuento, total, estado, notas)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (numero_factura, cliente_id, subtotal, descuento, total, estado, notas),
            )
            pedido_id = cur.lastrowid

            # Insertar ítems y descontar stock
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
                # Descontar stock (cantidad negativa = salida)
                ProductoModel.actualizar_stock(
                    item["producto_id"], -item["cantidad"], conn=conn
                )

            conn.commit()

        return numero_factura

    # ------------------------------------------------------------------ #
    #  Actualizar estado                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def actualizar_estado(pedido_id, nuevo_estado):
        """Cambia únicamente el campo 'estado' de un pedido."""
        with Database.get_connection() as conn:
            conn.execute(
                "UPDATE pedidos SET estado = ? WHERE id = ?",
                (nuevo_estado, pedido_id),
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    #  Consultas                                                           #
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
        # Convertir strings vacíos a None para evitar conflicto UNIQUE en documento
        documento  = documento.strip()  or None
        telefono   = telefono.strip()   or None
        email      = email.strip()      or None
        direccion  = direccion.strip()  or None
        with Database.get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO clientes (nombre, documento, telefono, email, direccion)
                   VALUES (?, ?, ?, ?, ?)""",
                (nombre, documento, telefono, email, direccion),
            )
            conn.commit()
            return cur.lastrowid