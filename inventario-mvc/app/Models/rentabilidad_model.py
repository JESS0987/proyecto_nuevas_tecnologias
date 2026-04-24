"""
Model: Rentabilidad
Cálculo automático de ganancias y reportes.
"""

from app.Models.database import Database


class RentabilidadModel:

    @staticmethod
    def ganancia_total(fecha_inicio=None, fecha_fin=None):
        sql = """
            SELECT
                SUM(ip.subtotal)                             AS ingresos,
                SUM(ip.costo_unitario * ip.cantidad)         AS costos,
                SUM(ip.subtotal
                    - ip.costo_unitario * ip.cantidad)       AS ganancia,
                COUNT(DISTINCT p.id)                         AS num_pedidos,
                SUM(ip.cantidad)                             AS unidades_vendidas
            FROM items_pedido ip
            JOIN pedidos p ON ip.pedido_id = p.id
        """
        params = []
        where  = []
        if fecha_inicio:
            where.append("date(p.fecha) >= ?")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("date(p.fecha) <= ?")
            params.append(fecha_fin)
        if where:
            sql += " WHERE " + " AND ".join(where)
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchone()

    @staticmethod
    def ganancia_hoy():
        return RentabilidadModel.ganancia_total(
            fecha_inicio="date('now')", fecha_fin="date('now')"
        )

    @staticmethod
    def ganancia_por_dia(anio=None, mes=None):
        sql = """
            SELECT
                date(p.fecha)                               AS dia,
                SUM(ip.subtotal
                    - ip.costo_unitario * ip.cantidad)      AS ganancia,
                SUM(ip.subtotal)                            AS ingresos,
                COUNT(DISTINCT p.id)                        AS pedidos
            FROM items_pedido ip
            JOIN pedidos p ON ip.pedido_id = p.id
        """
        params = []
        where  = []
        if anio:
            where.append("strftime('%Y', p.fecha) = ?")
            params.append(str(anio))
        if mes:
            where.append("strftime('%m', p.fecha) = ?")
            params.append(f"{mes:02d}")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " GROUP BY dia ORDER BY dia DESC LIMIT 30"
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    @staticmethod
    def ganancia_por_mes(anio=None):
        sql = """
            SELECT
                strftime('%Y-%m', p.fecha)                  AS mes,
                SUM(ip.subtotal
                    - ip.costo_unitario * ip.cantidad)      AS ganancia,
                SUM(ip.subtotal)                            AS ingresos,
                COUNT(DISTINCT p.id)                        AS pedidos,
                SUM(ip.cantidad)                            AS unidades
            FROM items_pedido ip
            JOIN pedidos p ON ip.pedido_id = p.id
        """
        params = []
        if anio:
            sql += " WHERE strftime('%Y', p.fecha) = ?"
            params.append(str(anio))
        sql += " GROUP BY mes ORDER BY mes DESC"
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    @staticmethod
    def desglose_mes(anio, mes):
        """
        Devuelve el detalle de productos vendidos en un mes específico:
        código, nombre, unidades, ingresos, costo total y ganancia.
        """
        sql = """
            SELECT
                pr.codigo,
                pr.nombre,
                SUM(ip.cantidad)                                AS unidades,
                SUM(ip.subtotal)                                AS ingresos,
                SUM(ip.costo_unitario * ip.cantidad)            AS costos,
                SUM(ip.subtotal - ip.costo_unitario*ip.cantidad) AS ganancia,
                ROUND(
                    SUM(ip.subtotal - ip.costo_unitario*ip.cantidad)
                    / NULLIF(SUM(ip.subtotal), 0) * 100, 1
                )                                               AS margen_pct
            FROM items_pedido ip
            JOIN productos pr ON ip.producto_id = pr.id
            JOIN pedidos   p  ON ip.pedido_id   = p.id
            WHERE strftime('%Y', p.fecha) = ?
              AND strftime('%m', p.fecha) = ?
              AND p.estado != 'cancelado'
            GROUP BY pr.id
            ORDER BY ganancia DESC
        """
        with Database.get_connection() as conn:
            return conn.execute(sql, (str(anio), f"{int(mes):02d}")).fetchall()

    @staticmethod
    def productos_mas_vendidos(limite=10, fecha_inicio=None, fecha_fin=None):
        sql = """
            SELECT
                pr.id, pr.codigo, pr.nombre,
                SUM(ip.cantidad)                             AS unidades_vendidas,
                SUM(ip.subtotal)                             AS ingresos,
                SUM(ip.subtotal
                    - ip.costo_unitario * ip.cantidad)       AS ganancia
            FROM items_pedido ip
            JOIN productos pr ON ip.producto_id = pr.id
            JOIN pedidos p    ON ip.pedido_id   = p.id
        """
        params = []
        where  = []
        if fecha_inicio:
            where.append("date(p.fecha) >= ?")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("date(p.fecha) <= ?")
            params.append(fecha_fin)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " GROUP BY pr.id ORDER BY unidades_vendidas DESC LIMIT ?"
        params.append(limite)
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    @staticmethod
    def ganancia_por_producto(fecha_inicio=None, fecha_fin=None):
        sql = """
            SELECT
                pr.id, pr.codigo, pr.nombre,
                pr.costo, pr.precio_venta,
                pr.precio_venta - pr.costo                  AS margen_unitario,
                ROUND(((pr.precio_venta - pr.costo)
                       / NULLIF(pr.costo, 0)) * 100, 2)     AS margen_pct,
                COALESCE(SUM(ip.cantidad), 0)               AS unidades_vendidas,
                COALESCE(SUM(ip.subtotal
                    - ip.costo_unitario * ip.cantidad), 0)  AS ganancia_total
            FROM productos pr
            LEFT JOIN items_pedido ip ON ip.producto_id = pr.id
            LEFT JOIN pedidos p       ON ip.pedido_id   = p.id
                  AND ({filtros})
            WHERE pr.activo = 1
            GROUP BY pr.id
            ORDER BY ganancia_total DESC
        """
        filtros_sql = "1=1"
        params = []
        if fecha_inicio:
            filtros_sql += " AND date(p.fecha) >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            filtros_sql += " AND date(p.fecha) <= ?"
            params.append(fecha_fin)
        sql = sql.format(filtros=filtros_sql)
        with Database.get_connection() as conn:
            return conn.execute(sql, params).fetchall()

    @staticmethod
    def resumen_inventario():
        sql = """
            SELECT
                COUNT(*)                                    AS total_productos,
                SUM(stock)                                  AS total_unidades,
                SUM(stock * costo)                          AS valor_costo,
                SUM(stock * precio_venta)                   AS valor_venta,
                SUM(stock * (precio_venta - costo))         AS ganancia_potencial
            FROM productos
            WHERE activo = 1
        """
        with Database.get_connection() as conn:
            return conn.execute(sql).fetchone()