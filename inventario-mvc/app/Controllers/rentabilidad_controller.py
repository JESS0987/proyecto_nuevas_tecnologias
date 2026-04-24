"""
Controller: Rentabilidad y Reportes
Cálculo de ganancias + exportación CSV.
"""

import csv
import os
import datetime
from app.Models.rentabilidad_model import RentabilidadModel
from config.settings import REPORTS_DIR


class RentabilidadController:

    @staticmethod
    def resumen_inventario():
        return RentabilidadModel.resumen_inventario()

    @staticmethod
    def ganancia_total(fecha_inicio=None, fecha_fin=None):
        return RentabilidadModel.ganancia_total(fecha_inicio, fecha_fin)

    @staticmethod
    def ganancia_por_dia(anio=None, mes=None):
        return RentabilidadModel.ganancia_por_dia(anio, mes)

    @staticmethod
    def ganancia_por_mes(anio=None):
        return RentabilidadModel.ganancia_por_mes(anio)

    @staticmethod
    def desglose_mes(mes_str):
        """
        Recibe un string 'YYYY-MM' y retorna el desglose de productos.
        """
        anio, mes = mes_str.split("-")
        return RentabilidadModel.desglose_mes(anio, mes)

    @staticmethod
    def productos_mas_vendidos(limite=10, fecha_inicio=None, fecha_fin=None):
        return RentabilidadModel.productos_mas_vendidos(limite, fecha_inicio, fecha_fin)

    @staticmethod
    def rentabilidad_por_producto(fecha_inicio=None, fecha_fin=None):
        return RentabilidadModel.ganancia_por_producto(fecha_inicio, fecha_fin)

    @staticmethod
    def exportar_reporte_csv(tipo="ventas_mes", fecha_inicio=None, fecha_fin=None):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = os.path.join(REPORTS_DIR, f"reporte_{tipo}_{ts}.csv")

        if tipo == "ventas_mes":
            datos  = RentabilidadModel.ganancia_por_mes()
            campos = ["mes", "ingresos", "ganancia", "pedidos", "unidades"]
            titulo = "Reporte de Ventas por Mes"
        elif tipo == "ventas_dia":
            datos  = RentabilidadModel.ganancia_por_dia()
            campos = ["dia", "ingresos", "ganancia", "pedidos"]
            titulo = "Reporte de Ventas por Día"
        elif tipo == "productos":
            datos  = RentabilidadModel.ganancia_por_producto(fecha_inicio, fecha_fin)
            campos = [
                "codigo", "nombre", "costo", "precio_venta",
                "margen_unitario", "margen_pct",
                "unidades_vendidas", "ganancia_total",
            ]
            titulo = "Reporte de Rentabilidad por Producto"
        elif tipo == "inventario":
            from app.Models.producto_model import ProductoModel
            datos  = ProductoModel.obtener_todos()
            campos = [
                "codigo", "nombre", "categoria_nombre",
                "costo", "precio_venta", "stock", "stock_minimo",
            ]
            titulo = "Reporte de Inventario"
        else:
            raise ValueError(f"Tipo de reporte desconocido: {tipo}")

        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([titulo])
            writer.writerow([f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            if fecha_inicio or fecha_fin:
                writer.writerow([f"Período: {fecha_inicio or ''} — {fecha_fin or ''}"])
            writer.writerow([])
            writer.writerow(campos)
            for fila in datos:
                writer.writerow([fila[c] if c in fila.keys() else "" for c in campos])

        return ruta