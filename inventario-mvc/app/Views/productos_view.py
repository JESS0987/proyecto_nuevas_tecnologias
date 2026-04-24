"""
View: Módulo de Inventario / Productos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from app.Views.widgets import TablaFrame, CampoForm, boton, BarraBusqueda, AlertaLabel
from app.Controllers.producto_controller import ProductoController
from config.settings import COLORS, FONTS


class ProductosView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["light"])
        self._producto_id = None
        self._build()
        self._cargar_tabla()

    # ------------------------------------------------------------------ #
    #  UI                                                                  #
    # ------------------------------------------------------------------ #

    def _build(self):
        # ── Encabezado ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["primary"], pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="📦  Gestión de Inventario",
            font=FONTS["title"], bg=COLORS["primary"], fg=COLORS["white"],
        ).pack(side="left", padx=20)

        # Indicador stock bajo
        self.lbl_alerta = tk.Label(
            header, text="", font=FONTS["small"],
            bg=COLORS["primary"], fg="#F1C40F",
        )
        self.lbl_alerta.pack(side="right", padx=20)

        # ── Barra de herramientas ────────────────────────────────────────
        toolbar = tk.Frame(self, bg=COLORS["light"], pady=6)
        toolbar.pack(fill="x", padx=10)

        boton(toolbar, "➕ Nuevo",   self._nuevo_producto,   "success").pack(side="left", padx=4)
        boton(toolbar, "✏️ Editar",  self._editar_producto,  "secondary").pack(side="left", padx=4)
        boton(toolbar, "🗑 Eliminar", self._eliminar_producto, "danger").pack(side="left", padx=4)
        boton(toolbar, "📥 Entrada", self._registrar_entrada, "warning").pack(side="left", padx=4)
        boton(toolbar, "🔄 Actualizar", self._cargar_tabla, "primary").pack(side="left", padx=4)

        self.barra_busqueda = BarraBusqueda(toolbar, "Buscar producto…", self._buscar)
        self.barra_busqueda.pack(side="right", padx=8)

        # ── Tabla ────────────────────────────────────────────────────────
        cols   = ["ID", "Código", "Nombre", "Categoría", "Costo", "P. Venta", "Stock", "Mín.", "Margen"]
        anchos = [40, 80, 180, 100, 80, 80, 60, 50, 80]
        self.tabla = TablaFrame(self, cols, anchos)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ------------------------------------------------------------------ #
    #  Tabla                                                               #
    # ------------------------------------------------------------------ #

    def _cargar_tabla(self, termino=""):
        self.tabla.limpiar()
        if termino and termino not in ("Buscar producto…", ""):
            productos = ProductoController.buscar_productos(termino)
        else:
            productos = ProductoController.listar_productos()

        for p in productos:
            margen = p["precio_venta"] - p["costo"]
            tag    = "alerta" if p["stock"] <= p["stock_minimo"] else None
            idx    = len(self.tabla.tree.get_children())
            auto_tag = "par" if idx % 2 == 0 else "impar"
            final_tag = tag or auto_tag
            self.tabla.tree.insert("", "end", iid=str(p["id"]), tags=(final_tag,), values=(
                p["id"], p["codigo"], p["nombre"],
                p["categoria_nombre"] or "—",
                f"${p['costo']:,.0f}", f"${p['precio_venta']:,.0f}",
                p["stock"], p["stock_minimo"],
                f"${margen:,.0f}",
            ))

        # Alerta stock bajo
        bajos = ProductoController.productos_stock_bajo()
        if bajos:
            self.lbl_alerta.config(text=f"⚠  {len(bajos)} producto(s) con stock bajo")
        else:
            self.lbl_alerta.config(text="✔  Stock OK")

    def _buscar(self, termino):
        self._cargar_tabla(termino)

    def _producto_seleccionado(self):
        sel = self.tabla.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla.")
            return None
        return int(sel[0])

    # ------------------------------------------------------------------ #
    #  Nuevo / Editar                                                      #
    # ------------------------------------------------------------------ #

    def _nuevo_producto(self):
        self._producto_id = None
        FormProducto(self, None, self._cargar_tabla)

    def _editar_producto(self):
        pid = self._producto_seleccionado()
        if pid is None:
            return
        producto = ProductoController.obtener_producto(pid)
        FormProducto(self, producto, self._cargar_tabla)

    def _eliminar_producto(self):
        pid = self._producto_seleccionado()
        if pid is None:
            return
        p = ProductoController.obtener_producto(pid)
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{p['nombre']}'?"):
            ProductoController.eliminar_producto(pid)
            self._cargar_tabla()
            messagebox.showinfo("Listo", "Producto eliminado.")

    # ------------------------------------------------------------------ #
    #  Entrada de inventario                                               #
    # ------------------------------------------------------------------ #

    def _registrar_entrada(self):
        pid = self._producto_seleccionado()
        if pid is None:
            return
        p = ProductoController.obtener_producto(pid)
        FormEntrada(self, p, self._cargar_tabla)


# ====================================================================== #
#  Diálogo: Formulario de Producto                                        #
# ====================================================================== #

class FormProducto(tk.Toplevel):

    def __init__(self, parent, producto, callback):
        super().__init__(parent)
        self.producto = producto
        self.callback = callback
        self.title("Nuevo Producto" if not producto else "Editar Producto")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=COLORS["white"])
        self._build()
        if producto:
            self._rellenar(producto)
        self.focus()

    def _build(self):
        pad = {"padx": 16, "pady": 6}
        tk.Label(
            self,
            text=("Nuevo Producto" if not self.producto else "Editar Producto"),
            font=FONTS["heading"], bg=COLORS["white"], fg=COLORS["primary"],
        ).pack(**pad)
        ttk.Separator(self).pack(fill="x", padx=16)

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=16, pady=8)

        self.f_codigo      = CampoForm(form, "Código",       requerido=True)
        self.f_nombre      = CampoForm(form, "Nombre",       requerido=True)
        self.f_descripcion = CampoForm(form, "Descripción")
        self.f_costo       = CampoForm(form, "Costo ($)",    requerido=True)
        self.f_precio      = CampoForm(form, "Precio venta", requerido=True)
        self.f_stock       = CampoForm(form, "Stock inicial",requerido=True)
        self.f_stock_min   = CampoForm(form, "Stock mínimo")

        for w in [self.f_codigo, self.f_nombre, self.f_descripcion,
                  self.f_costo, self.f_precio, self.f_stock, self.f_stock_min]:
            w.pack(fill="x", pady=3)

        # Categoría
        cat_frame = tk.Frame(form, bg=COLORS["white"])
        cat_frame.pack(fill="x", pady=3)
        tk.Label(cat_frame, text="Categoría", font=FONTS["normal"],
                 bg=COLORS["white"], width=16, anchor="w").pack(side="left")
        categorias = ProductoController.listar_categorias()
        self._cat_map = {c["nombre"]: c["id"] for c in categorias}
        self.cat_var = tk.StringVar(value=list(self._cat_map.keys())[0])
        ttk.Combobox(
            cat_frame, textvariable=self.cat_var,
            values=list(self._cat_map.keys()), state="readonly", width=22,
        ).pack(side="left", padx=4)

        self.alerta = AlertaLabel(self)
        self.alerta.pack(padx=16)

        # Botones
        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(pady=12)
        boton(btn_frame, "💾 Guardar",   self._guardar, "success").pack(side="left", padx=6)
        boton(btn_frame, "✖ Cancelar", self.destroy,   "danger").pack(side="left", padx=6)

    def _rellenar(self, p):
        self.f_codigo.set(p["codigo"])
        self.f_nombre.set(p["nombre"])
        self.f_descripcion.set(p["descripcion"] or "")
        self.f_costo.set(str(p["costo"]))
        self.f_precio.set(str(p["precio_venta"]))
        self.f_stock.set(str(p["stock"]))
        self.f_stock_min.set(str(p["stock_minimo"]))
        if p["categoria_nombre"] in self._cat_map:
            self.cat_var.set(p["categoria_nombre"])

    def _guardar(self):
        self.alerta.limpiar()
        datos = {
            "codigo":      self.f_codigo.get(),
            "nombre":      self.f_nombre.get(),
            "descripcion": self.f_descripcion.get(),
            "costo":       self.f_costo.get(),
            "precio_venta":self.f_precio.get(),
            "stock":       self.f_stock.get(),
            "stock_minimo":self.f_stock_min.get() or "5",
            "categoria_id":self._cat_map.get(self.cat_var.get()),
        }
        try:
            if self.producto:
                ProductoController.actualizar_producto(self.producto["id"], datos)
                msg = "Producto actualizado correctamente."
            else:
                ProductoController.crear_producto(datos)
                msg = "Producto creado correctamente."
            self.callback()
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        except ValueError as e:
            self.alerta.error(str(e))


# ====================================================================== #
#  Diálogo: Entrada de inventario                                         #
# ====================================================================== #

class FormEntrada(tk.Toplevel):

    def __init__(self, parent, producto, callback):
        super().__init__(parent)
        self.producto = producto
        self.callback = callback
        self.title(f"Entrada — {producto['nombre']}")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg=COLORS["white"])
        self._build()
        self.focus()

    def _build(self):
        pad = {"padx": 16, "pady": 6}
        tk.Label(
            self,
            text=f"Registrar Entrada\n{self.producto['nombre']}",
            font=FONTS["heading"], bg=COLORS["white"], fg=COLORS["primary"],
            justify="center",
        ).pack(**pad)
        tk.Label(
            self,
            text=f"Stock actual: {self.producto['stock']}",
            font=FONTS["normal"], bg=COLORS["white"], fg=COLORS["text_light"],
        ).pack()
        ttk.Separator(self).pack(fill="x", padx=16, pady=4)

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=16)
        self.f_cantidad  = CampoForm(form, "Cantidad",      requerido=True)
        self.f_costo     = CampoForm(form, "Costo unitario",requerido=True)
        self.f_proveedor = CampoForm(form, "Proveedor")
        self.f_notas     = CampoForm(form, "Notas")
        for w in [self.f_cantidad, self.f_costo, self.f_proveedor, self.f_notas]:
            w.pack(fill="x", pady=3)

        self.f_costo.set(str(self.producto["costo"]))

        self.alerta = AlertaLabel(self)
        self.alerta.pack(padx=16)

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(pady=12)
        boton(btn_frame, "📥 Registrar", self._guardar, "success").pack(side="left", padx=6)
        boton(btn_frame, "✖ Cancelar",  self.destroy,  "danger").pack(side="left", padx=6)

    def _guardar(self):
        self.alerta.limpiar()
        try:
            cantidad = int(self.f_cantidad.get())
            costo    = float(self.f_costo.get())
        except ValueError:
            self.alerta.error("Cantidad y costo deben ser números válidos.")
            return
        try:
            ProductoController.registrar_entrada(
                self.producto["id"], cantidad, costo,
                self.f_proveedor.get(), self.f_notas.get(),
            )
            self.callback()
            messagebox.showinfo("Éxito", f"Se agregaron {cantidad} unidades al inventario.")
            self.destroy()
        except ValueError as e:
            self.alerta.error(str(e))
