"""
View: Módulo de Rentabilidad y Reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from app.Views.widgets import TablaFrame, boton, AlertaLabel
from app.Controllers.rentabilidad_controller import RentabilidadController
from config.settings import COLORS, FONTS


class RentabilidadView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["light"])
        self._build()
        self._cargar_resumen()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["primary"], pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="📊  Rentabilidad y Reportes",
            font=FONTS["title"], bg=COLORS["primary"], fg=COLORS["white"],
        ).pack(side="left", padx=20)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_resumen   = tk.Frame(self.tabs, bg=COLORS["white"])
        self.tab_mensual   = tk.Frame(self.tabs, bg=COLORS["white"])
        self.tab_productos = tk.Frame(self.tabs, bg=COLORS["white"])
        self.tab_exportar  = tk.Frame(self.tabs, bg=COLORS["white"])

        self.tabs.add(self.tab_resumen,   text="  Resumen General  ")
        self.tabs.add(self.tab_mensual,   text="  Por Mes  ")
        self.tabs.add(self.tab_productos, text="  Por Producto  ")
        self.tabs.add(self.tab_exportar,  text="  Exportar  ")

        self._build_resumen()
        self._build_mensual()
        self._build_productos()
        self._build_exportar()

    # ------------------------------------------------------------------ #
    #  Tab Resumen                                                         #
    # ------------------------------------------------------------------ #

    def _build_resumen(self):
        pad = {"padx": 20, "pady": 10}
        tk.Label(self.tab_resumen, text="Resumen de Inventario",
                 font=FONTS["heading"], bg=COLORS["white"],
                 fg=COLORS["primary"]).pack(**pad)

        self.cards_frame = tk.Frame(self.tab_resumen, bg=COLORS["white"])
        self.cards_frame.pack(fill="x", padx=20)

        filtro = tk.Frame(self.tab_resumen, bg=COLORS["white"])
        filtro.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(filtro, text="Período:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.ini_var = tk.StringVar(value=datetime.date.today().replace(day=1).isoformat())
        self.fin_var = tk.StringVar(value=datetime.date.today().isoformat())
        tk.Entry(filtro, textvariable=self.ini_var, width=12, font=FONTS["small"]).pack(side="left", padx=4)
        tk.Label(filtro, text="→", bg=COLORS["white"]).pack(side="left")
        tk.Entry(filtro, textvariable=self.fin_var, width=12, font=FONTS["small"]).pack(side="left", padx=4)
        boton(filtro, "Calcular", self._cargar_resumen, "primary").pack(side="left", padx=8)

        tk.Label(self.tab_resumen, text="Ganancia del período",
                 font=FONTS["normal"], bg=COLORS["white"],
                 fg=COLORS["text_light"]).pack(padx=20, anchor="w")
        cols   = ["Métrica", "Valor"]
        anchos = [220, 180]
        self.tabla_resumen = TablaFrame(self.tab_resumen, cols, anchos)
        self.tabla_resumen.pack(fill="both", expand=True, padx=20, pady=10)

    def _cargar_resumen(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        inv = RentabilidadController.resumen_inventario()
        if inv:
            metricas = [
                ("Productos",    inv["total_productos"],                        "secondary"),
                ("Unidades",     inv["total_unidades"] or 0,                    "primary"),
                ("Valor Costo",  f"${(inv['valor_costo'] or 0):,.0f}",          "warning"),
                ("Valor Venta",  f"${(inv['valor_venta'] or 0):,.0f}",          "success"),
                ("G. Potencial", f"${(inv['ganancia_potencial'] or 0):,.0f}",   "danger"),
            ]
            for etiqueta, valor, color in metricas:
                self._card(self.cards_frame, etiqueta, valor, color).pack(
                    side="left", padx=6, pady=6)

        self.tabla_resumen.limpiar()
        ini = self.ini_var.get() or None
        fin = self.fin_var.get() or None
        g   = RentabilidadController.ganancia_total(ini, fin)
        if g:
            rows = [
                ("Ingresos totales",  f"${(g['ingresos'] or 0):,.0f}"),
                ("Costos totales",    f"${(g['costos'] or 0):,.0f}"),
                ("Ganancia bruta",    f"${(g['ganancia'] or 0):,.0f}"),
                ("N° pedidos",        g["num_pedidos"] or 0),
                ("Unidades vendidas", g["unidades_vendidas"] or 0),
            ]
            for r in rows:
                self.tabla_resumen.tree.insert("", "end", values=r)

    def _card(self, parent, titulo, valor, color):
        frame = tk.Frame(parent, bg=COLORS.get(color, COLORS["secondary"]),
                         padx=18, pady=12)
        tk.Label(frame, text=str(valor), font=("Helvetica", 18, "bold"),
                 bg=COLORS.get(color), fg=COLORS["white"]).pack()
        tk.Label(frame, text=titulo, font=FONTS["small"],
                 bg=COLORS.get(color), fg=COLORS["white"]).pack()
        return frame

    # ------------------------------------------------------------------ #
    #  Tab Mensual                                                         #
    # ------------------------------------------------------------------ #

    def _build_mensual(self):
        # Panel izquierdo: tabla de meses
        paned = tk.PanedWindow(self.tab_mensual, orient="horizontal",
                               bg=COLORS["white"], sashwidth=6)
        paned.pack(fill="both", expand=True, padx=10, pady=8)

        left = tk.Frame(paned, bg=COLORS["white"])
        paned.add(left, minsize=320)

        right = tk.Frame(paned, bg=COLORS["white"])
        paned.add(right, minsize=380)

        # ── Lado izquierdo: filtro + tabla meses ──
        toolbar = tk.Frame(left, bg=COLORS["white"], pady=8)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Año:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.anio_var = tk.StringVar(value=str(datetime.date.today().year))
        tk.Entry(toolbar, textvariable=self.anio_var, width=6,
                 font=FONTS["normal"]).pack(side="left", padx=4)
        boton(toolbar, "Ver", self._cargar_mensual, "primary").pack(side="left", padx=8)

        cols   = ["Mes", "Ingresos", "Ganancia", "Pedidos", "Unidades"]
        anchos = [90, 100, 100, 65, 65]
        self.tabla_mensual = TablaFrame(left, cols, anchos)
        self.tabla_mensual.pack(fill="both", expand=True)
        self.tabla_mensual.tree.bind("<<TreeviewSelect>>", self._on_mes_seleccionado)

        tk.Label(left, text="↑ Haz clic en un mes para ver el desglose",
                 font=FONTS["small"], bg=COLORS["white"],
                 fg=COLORS["text_light"]).pack(pady=(4, 0))

        # ── Lado derecho: desglose del mes ──
        self.lbl_desglose = tk.Label(right, text="Selecciona un mes",
                                     font=FONTS["heading"], bg=COLORS["white"],
                                     fg=COLORS["primary"])
        self.lbl_desglose.pack(pady=(8, 4), padx=8, anchor="w")

        cols2   = ["Producto", "Unid.", "Ingresos", "Costo", "Ganancia", "Margen%"]
        anchos2 = [170, 45, 90, 90, 90, 65]
        self.tabla_desglose = TablaFrame(right, cols2, anchos2)
        self.tabla_desglose.pack(fill="both", expand=True, padx=4)

        # Totales del desglose
        self.lbl_totales = tk.Label(right, text="", font=FONTS["normal"],
                                    bg=COLORS["white"], fg=COLORS["primary"],
                                    justify="left", anchor="w")
        self.lbl_totales.pack(padx=8, pady=6, anchor="w")

        self._cargar_mensual()

    def _cargar_mensual(self):
        self.tabla_mensual.limpiar()
        self.tabla_desglose.limpiar()
        self.lbl_desglose.config(text="Selecciona un mes")
        self.lbl_totales.config(text="")
        anio  = self.anio_var.get() or None
        datos = RentabilidadController.ganancia_por_mes(anio)
        for d in datos:
            idx = len(self.tabla_mensual.tree.get_children())
            tag = "par" if idx % 2 == 0 else "impar"
            self.tabla_mensual.tree.insert("", "end", iid=d["mes"], tags=(tag,), values=(
                d["mes"],
                f"${(d['ingresos'] or 0):,.0f}",
                f"${(d['ganancia'] or 0):,.0f}",
                d["pedidos"] or 0,
                d["unidades"] or 0,
            ))

    def _on_mes_seleccionado(self, event=None):
        sel = self.tabla_mensual.tree.selection()
        if not sel:
            return
        mes_str = sel[0]  # formato 'YYYY-MM'
        self._cargar_desglose(mes_str)

    def _cargar_desglose(self, mes_str):
        self.tabla_desglose.limpiar()
        self.lbl_desglose.config(text=f"Desglose: {mes_str}")
        datos = RentabilidadController.desglose_mes(mes_str)

        total_ingresos = 0
        total_costos   = 0
        total_ganancia = 0
        total_unidades = 0

        for d in datos:
            idx = len(self.tabla_desglose.tree.get_children())
            tag = "par" if idx % 2 == 0 else "impar"
            self.tabla_desglose.tree.insert("", "end", tags=(tag,), values=(
                d["nombre"],
                d["unidades"] or 0,
                f"${(d['ingresos'] or 0):,.0f}",
                f"${(d['costos'] or 0):,.0f}",
                f"${(d['ganancia'] or 0):,.0f}",
                f"{d['margen_pct'] or 0:.1f}%",
            ))
            total_ingresos += d["ingresos"] or 0
            total_costos   += d["costos"]   or 0
            total_ganancia += d["ganancia"] or 0
            total_unidades += d["unidades"] or 0

        if datos:
            self.lbl_totales.config(
                text=(
                    f"Total unidades: {total_unidades}   |   "
                    f"Ingresos: ${total_ingresos:,.0f}   |   "
                    f"Costos: ${total_costos:,.0f}   |   "
                    f"Ganancia: ${total_ganancia:,.0f}"
                )
            )
        else:
            self.lbl_totales.config(text="Sin ventas registradas en este mes.")

    # ------------------------------------------------------------------ #
    #  Tab Productos                                                       #
    # ------------------------------------------------------------------ #

    def _build_productos(self):
        toolbar = tk.Frame(self.tab_productos, bg=COLORS["white"], pady=8)
        toolbar.pack(fill="x", padx=16)
        tk.Label(toolbar, text="Top:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.top_var = tk.StringVar(value="10")
        ttk.Combobox(
            toolbar, textvariable=self.top_var,
            values=["5", "10", "20", "50"], state="readonly", width=5
        ).pack(side="left", padx=4)
        boton(toolbar, "Ver", self._cargar_productos, "primary").pack(side="left", padx=8)

        cols   = ["Código", "Nombre", "Unid. Vendidas", "Ingresos", "Ganancia", "Margen %", "Stock"]
        anchos = [70, 200, 100, 100, 100, 80, 60]
        self.tabla_productos = TablaFrame(self.tab_productos, cols, anchos)
        self.tabla_productos.pack(fill="both", expand=True, padx=16, pady=10)
        self._cargar_productos()

    def _cargar_productos(self):
        self.tabla_productos.limpiar()
        limite = int(self.top_var.get() or 10)
        datos  = RentabilidadController.rentabilidad_por_producto()[:limite]
        for d in datos:
            from app.Models.producto_model import ProductoModel
            prod  = ProductoModel.obtener_por_id(d["id"])
            stock = prod["stock"] if prod else "—"
            idx   = len(self.tabla_productos.tree.get_children())
            tag   = "par" if idx % 2 == 0 else "impar"
            self.tabla_productos.tree.insert("", "end", tags=(tag,), values=(
                d["codigo"], d["nombre"],
                d["unidades_vendidas"] or 0,
                f"${(d['ganancia_total'] or 0):,.0f}",
                f"${(d['ganancia_total'] or 0):,.0f}",
                f"{d['margen_pct'] or 0:.1f}%",
                stock,
            ))

    # ------------------------------------------------------------------ #
    #  Tab Exportar                                                        #
    # ------------------------------------------------------------------ #

    def _build_exportar(self):
        frame = tk.Frame(self.tab_exportar, bg=COLORS["white"])
        frame.pack(expand=True)

        tk.Label(frame, text="Exportar Reportes CSV",
                 font=FONTS["heading"], bg=COLORS["white"],
                 fg=COLORS["primary"]).pack(pady=20)

        reportes = [
            ("📅 Ventas por Mes",         "ventas_mes"),
            ("📆 Ventas por Día",         "ventas_dia"),
            ("💰 Rentabilidad Productos", "productos"),
            ("📦 Inventario Actual",      "inventario"),
        ]
        for texto, tipo in reportes:
            boton(
                frame, texto,
                lambda t=tipo: self._exportar(t),
                "secondary"
            ).pack(fill="x", padx=40, pady=6, ipady=8)

        self.alerta_export = AlertaLabel(frame)
        self.alerta_export.pack(pady=10)

    def _exportar(self, tipo):
        self.alerta_export.limpiar()
        try:
            ruta = RentabilidadController.exportar_reporte_csv(tipo)
            self.alerta_export.ok(f"Guardado en: {ruta}")
            messagebox.showinfo("Exportado", f"Reporte guardado en:\n{ruta}")
        except Exception as e:
            self.alerta_export.error(str(e))