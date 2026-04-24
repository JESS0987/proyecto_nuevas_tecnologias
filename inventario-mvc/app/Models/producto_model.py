"""
Model: Producto
Lógica de datos para productos e inventario.
"""

from app.Models.database import Database


class ProductoModel:

    # ------------------------------------------------------------------ #
    #  CRUD básico                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def obtener_todos(solo_activos=True):
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
        """
        if solo_activos:
            sql += " WHERE p.activo = 1"
        sql += " ORDER BY p.nombre"
        with Database.get_connection() as conn:
            return conn.execute(sql).fetchall()

    @staticmethod
    def obtener_por_id(producto_id):
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = ?
        """
        with Database.get_connection() as conn:
            return conn.execute(sql, (producto_id,)).fetchone()

    @staticmethod
    def obtener_por_codigo(codigo):
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.codigo = ? AND p.activo = 1
        """
        with Database.get_connection() as conn:
            return conn.execute(sql, (codigo,)).fetchone()

    @staticmethod
    def buscar(termino):
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
              AND (p.nombre LIKE ? OR p.codigo LIKE ? OR c.nombre LIKE ?)
            ORDER BY p.nombre
        """
        t = f"%{termino}%"
        with Database.get_connection() as conn:
            return conn.execute(sql, (t, t, t)).fetchall()

    @staticmethod
    def crear(codigo, nombre, descripcion, categoria_id,
              costo, precio_venta, stock, stock_minimo):
        sql = """
            INSERT INTO productos
                (codigo, nombre, descripcion, categoria_id,
                 costo, precio_venta, stock, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with Database.get_connection() as conn:
            cur = conn.execute(
                sql, (codigo, nombre, descripcion, categoria_id,
                      costo, precio_venta, stock, stock_minimo)
            )
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def actualizar(producto_id, codigo, nombre, descripcion, categoria_id,
                   costo, precio_venta, stock, stock_minimo):
        sql = """
            UPDATE productos
            SET codigo=?, nombre=?, descripcion=?, categoria_id=?,
                costo=?, precio_venta=?, stock=?, stock_minimo=?,
                actualizado_en=CURRENT_TIMESTAMP
            WHERE id=?
        """
        with Database.get_connection() as conn:
            conn.execute(
                sql, (codigo, nombre, descripcion, categoria_id,
                      costo, precio_venta, stock, stock_minimo, producto_id)
            )
            conn.commit()

    @staticmethod
    def eliminar(producto_id):
        """Eliminación lógica (desactivar)."""
        with Database.get_connection() as conn:
            conn.execute(
                "UPDATE productos SET activo=0 WHERE id=?", (producto_id,)
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    #  Stock                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def actualizar_stock(producto_id, cantidad, conn=None):
        """
        Descuenta stock. Pasa conn externo si quieres incluirlo en una
        transacción mayor (p.ej. al registrar un pedido).
        """
        sql = """
            UPDATE productos
            SET stock = stock + ?,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        if conn:
            conn.execute(sql, (cantidad, producto_id))
        else:
            with Database.get_connection() as conn2:
                conn2.execute(sql, (cantidad, producto_id))
                conn2.commit()

    @staticmethod
    def con_stock_bajo():
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1 AND p.stock <= p.stock_minimo
            ORDER BY p.stock ASC
        """
        with Database.get_connection() as conn:
            return conn.execute(sql).fetchall()

    # ------------------------------------------------------------------ #
    #  Entradas de inventario (compras)                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def registrar_entrada(producto_id, cantidad, costo_unitario,
                          proveedor="", notas=""):
        with Database.get_connection() as conn:
            conn.execute(
                """INSERT INTO entradas_inventario
                   (producto_id, cantidad, costo_unitario, proveedor, notas)
                   VALUES (?, ?, ?, ?, ?)""",
                (producto_id, cantidad, costo_unitario, proveedor, notas),
            )
            conn.execute(
                """UPDATE productos
                   SET stock = stock + ?,
                       costo = ?,
                       actualizado_en = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (cantidad, costo_unitario, producto_id),
            )
            conn.commit()

    @staticmethod
    def historial_entradas(producto_id=None):
        sql = """
            SELECT e.*, p.nombre AS producto_nombre, p.codigo
            FROM entradas_inventario e
            JOIN productos p ON e.producto_id = p.id
        """
        params = ()
        if producto_id:
            sql += " WHERE e.producto_id = ?"
            params = (producto_id,)
        sql += " ORDER BY e.fecha DESC"
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    # ------------------------------------------------------------------ #
    #  Categorías                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def obtener_categorias():
        with Database.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM categorias ORDER BY nombre"
            ).fetchall()
