"""
View: Módulo de Ventas / Pedidos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from app.Views.widgets import TablaFrame, CampoForm, boton, AlertaLabel
from app.Controllers.pedido_controller import PedidoController
from app.Controllers.producto_controller import ProductoController
from config.settings import COLORS, FONTS


# Colores y etiquetas por estado
ESTADO_COLOR_BG = {
    "pendiente":  "#FFF9C4",
    "despachado": "#E8F5E9",
    "cancelado":  "#FFEBEE",
}
ESTADO_COLOR_FG = {
    "pendiente":  "#7B6000",
    "despachado": "#1B5E20",
    "cancelado":  "#B71C1C",
}
ESTADO_ICONO = {
    "pendiente":  "🕐 Pendiente",
    "despachado": "✅ Despachado",
    "cancelado":  "❌ Cancelado",
}
ESTADO_DESC = {
    "pendiente":  "Registrado, aún sin entregar al cliente.",
    "despachado": "Entregado al cliente correctamente.",
    "cancelado":  "Pedido anulado.",
}


class VentasView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["light"])
        self._todos_pedidos = []
        self._build()
        self._cargar_tabla()

    def _build(self):
        # ── Encabezado ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["primary"], pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="🛒  Módulo de Ventas",
            font=FONTS["title"], bg=COLORS["primary"], fg=COLORS["white"],
        ).pack(side="left", padx=20)

        # ── Toolbar ─────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=COLORS["light"], pady=6)
        toolbar.pack(fill="x", padx=10)
        boton(toolbar, "➕ Nueva Venta",    self._nueva_venta,    "success").pack(side="left", padx=4)
        boton(toolbar, "🧾 Ver Factura",    self._ver_factura,    "secondary").pack(side="left", padx=4)
        boton(toolbar, "🔄 Actualizar",     self._cargar_tabla,   "primary").pack(side="left", padx=4)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)
        boton(toolbar, "✏️ Cambiar Estado", self._cambiar_estado, "warning").pack(side="left", padx=4)

        # ── Barra de filtros ─────────────────────────────────────────────
        filtros = tk.Frame(self, bg=COLORS["white"], pady=6, relief="groove", bd=1)
        filtros.pack(fill="x", padx=10, pady=(0, 4))

        tk.Label(filtros, text="  Filtrar:",
                 font=FONTS["normal"], bg=COLORS["white"],
                 fg=COLORS["text_dark"]).pack(side="left", padx=(4, 8))

        self._filtro_btns   = {}
        self._filtro_activo = "todos"

        opciones = [
            ("todos",      "Todos",                   COLORS["light"],             COLORS["text_dark"]),
            ("pendiente",  ESTADO_ICONO["pendiente"],  ESTADO_COLOR_BG["pendiente"],  ESTADO_COLOR_FG["pendiente"]),
            ("despachado", ESTADO_ICONO["despachado"], ESTADO_COLOR_BG["despachado"], ESTADO_COLOR_FG["despachado"]),
            ("cancelado",  ESTADO_ICONO["cancelado"],  ESTADO_COLOR_BG["cancelado"],  ESTADO_COLOR_FG["cancelado"]),
        ]

        for clave, etiqueta, bg, fg in opciones:
            btn = tk.Button(
                filtros, text=etiqueta,
                font=FONTS["small"],
                bg=bg, fg=fg,
                activebackground=bg, activeforeground=fg,
                relief="solid", bd=1,
                padx=10, pady=3,
                cursor="hand2",
                command=lambda c=clave: self._aplicar_filtro(c),
            )
            btn.pack(side="left", padx=3)
            self._filtro_btns[clave] = btn

        self.lbl_conteo = tk.Label(filtros, text="",
                                   font=FONTS["small"],
                                   bg=COLORS["white"],
                                   fg=COLORS["text_light"])
        self.lbl_conteo.pack(side="right", padx=12)

        self._marcar_filtro_activo("todos")

        # ── Tabla ────────────────────────────────────────────────────────
        cols   = ["ID", "Factura", "Cliente", "Fecha", "Subtotal", "Descuento", "Total", "Estado"]
        anchos = [40,   130,       160,        140,     90,         80,          90,      120]
        self.tabla = TablaFrame(self, cols, anchos)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for estado, color in ESTADO_COLOR_BG.items():
            self.tabla.tree.tag_configure(estado, background=color,
                                          foreground=ESTADO_COLOR_FG[estado])

    # ------------------------------------------------------------------ #
    #  Filtros                                                             #
    # ------------------------------------------------------------------ #

    def _marcar_filtro_activo(self, clave):
        for k, btn in self._filtro_btns.items():
            btn.config(relief="sunken" if k == clave else "solid",
                       bd=2 if k == clave else 1)
        self._filtro_activo = clave

    def _aplicar_filtro(self, clave):
        self._marcar_filtro_activo(clave)
        pedidos = self._todos_pedidos if clave == "todos" else [
            p for p in self._todos_pedidos if p["estado"].lower() == clave
        ]
        self._renderizar_tabla(pedidos)

    # ------------------------------------------------------------------ #
    #  Carga de datos                                                      #
    # ------------------------------------------------------------------ #

    def _cargar_tabla(self):
        self._todos_pedidos = PedidoController.listar_pedidos()
        self._aplicar_filtro(self._filtro_activo)

    def _renderizar_tabla(self, pedidos):
        self.tabla.limpiar()
        for idx, p in enumerate(pedidos):
            estado = p["estado"].lower()
            tag    = estado if estado in ESTADO_COLOR_BG else ("par" if idx % 2 == 0 else "impar")
            self.tabla.tree.insert("", "end", iid=str(p["id"]), tags=(tag,), values=(
                p["id"],
                p["numero_factura"],
                p["cliente_nombre"] or "Consumidor Final",
                p["fecha"][:16],
                f"${p['subtotal']:,.0f}",
                f"${p['descuento']:,.0f}",
                f"${p['total']:,.0f}",
                ESTADO_ICONO.get(estado, estado.capitalize()),
            ))
        n = len(pedidos)
        self.lbl_conteo.config(text=f"{n} pedido{'s' if n != 1 else ''}")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _pedido_seleccionado(self):
        sel = self.tabla.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pedido.")
            return None
        return int(sel[0])

    # ------------------------------------------------------------------ #
    #  Acciones                                                            #
    # ------------------------------------------------------------------ #

    def _nueva_venta(self):
        NuevaVentaDialog(self, self._cargar_tabla)

    def _ver_factura(self):
        pid = self._pedido_seleccionado()
        if pid is None:
            return
        pedido, _ = PedidoController.obtener_pedido(pid)
        texto = PedidoController.generar_texto_factura(pedido["numero_factura"])
        FacturaDialog(self, texto)

    def _cambiar_estado(self):
        pid = self._pedido_seleccionado()
        if pid is None:
            return
        pedido, _ = PedidoController.obtener_pedido(pid)
        if not pedido:
            messagebox.showerror("Error", "Pedido no encontrado.")
            return
        CambiarEstadoDialog(self, pedido, callback=self._cargar_tabla)


# ====================================================================== #
#  Diálogo: Cambiar Estado                                                #
# ====================================================================== #

class CambiarEstadoDialog(tk.Toplevel):

    ESTADOS = ["pendiente", "despachado", "cancelado"]

    def __init__(self, parent, pedido, callback):
        super().__init__(parent)
        self.pedido         = pedido
        self.callback       = callback
        self.estado_elegido = pedido["estado"].lower()   # str simple, sin StringVar

        self.title("Cambiar Estado del Pedido")
        self.geometry("430x320")
        self.resizable(False, False)
        self.configure(bg=COLORS["white"])
        self.grab_set()
        self._build()
        self.focus()

    def _build(self):
        # ── Cabecera ────────────────────────────────────────────────────
        cab = tk.Frame(self, bg=COLORS["primary"], pady=10)
        cab.pack(fill="x")
        tk.Label(cab,
                 text=f"  Factura: {self.pedido['numero_factura']}",
                 font=FONTS["heading"], bg=COLORS["primary"],
                 fg=COLORS["white"]).pack(side="left")

        estado_actual = self.pedido["estado"].lower()
        tk.Label(cab,
                 text=f"  {ESTADO_ICONO.get(estado_actual, estado_actual)}  ",
                 font=FONTS["small"],
                 bg=ESTADO_COLOR_BG.get(estado_actual, COLORS["light"]),
                 fg=ESTADO_COLOR_FG.get(estado_actual, COLORS["text_dark"])).pack(side="right", padx=12)

        # ── Cliente ─────────────────────────────────────────────────────
        try:
            cliente = self.pedido["cliente_nombre"] or "Consumidor Final"
        except (IndexError, KeyError):
            cliente = "Consumidor Final"
        tk.Label(self,
                 text=f"Cliente: {cliente}",
                 font=FONTS["normal"], bg=COLORS["white"],
                 fg=COLORS["text_dark"]).pack(padx=16, pady=(10, 2), anchor="w")

        tk.Label(self, text="Seleccione el nuevo estado:",
                 font=FONTS["normal"], bg=COLORS["white"],
                 fg=COLORS["text_dark"]).pack(padx=16, pady=(0, 6), anchor="w")

        # ── Tarjetas clickeables (en vez de Radiobutton) ─────────────────
        # Los Radiobutton de tkinter en Windows muestran un recuadro blanco
        # sobre fondos de color. Usamos tk.Button con lógica manual de
        # selección para evitar ese bug.
        self._tarjetas = {}   # estado -> (frame, btn)
        contenedor = tk.Frame(self, bg=COLORS["white"])
        contenedor.pack(fill="x", padx=16, pady=0)

        for estado in self.ESTADOS:
            bg  = ESTADO_COLOR_BG[estado]
            fg  = ESTADO_COLOR_FG[estado]

            card = tk.Frame(contenedor, bg=bg, relief="solid", bd=1)
            card.pack(fill="x", pady=3)

            btn = tk.Button(
                card,
                text=f"  {ESTADO_ICONO[estado]}   —   {ESTADO_DESC[estado]}",
                font=FONTS["normal"],
                bg=bg, fg=fg,
                activebackground=bg, activeforeground=fg,
                relief="flat",
                anchor="w",
                padx=10, pady=7,
                cursor="hand2",
                command=lambda e=estado: self._seleccionar(e),
            )
            btn.pack(fill="x")
            self._tarjetas[estado] = (card, btn)

        self._refrescar_tarjetas()

        # ── Botones ──────────────────────────────────────────────────────
        acc = tk.Frame(self, bg=COLORS["white"])
        acc.pack(pady=10)
        boton(acc, "✔ Guardar",  self._guardar, "success").pack(side="left", padx=6)
        boton(acc, "✖ Cancelar", self.destroy,  "danger").pack(side="left", padx=6)

    def _seleccionar(self, estado):
        self.estado_elegido = estado
        self._refrescar_tarjetas()

    def _refrescar_tarjetas(self):
        """Resalta la tarjeta activa con borde grueso, el resto queda fino."""
        familia = FONTS["normal"][0]
        tamanio = FONTS["normal"][1]
        for estado, (card, btn) in self._tarjetas.items():
            if estado == self.estado_elegido:
                card.config(bd=3)
                btn.config(font=f"{familia} {tamanio} bold")
            else:
                card.config(bd=1)
                btn.config(font=f"{familia} {tamanio}")

    def _guardar(self):
        nuevo  = self.estado_elegido
        actual = self.pedido["estado"].lower()

        if nuevo == actual:
            messagebox.showinfo("Sin cambios",
                                "El estado seleccionado ya es el actual.")
            return

        if nuevo == "cancelado":
            ok = messagebox.askyesno(
                "Confirmar cancelación",
                f"¿Cancelar la factura {self.pedido['numero_factura']}?\n"
                "Esta acción no revierte el stock automáticamente.",
                icon="warning",
            )
            if not ok:
                return

        try:
            PedidoController.cambiar_estado(self.pedido["id"], nuevo)
            messagebox.showinfo(
                "Listo",
                f"Factura {self.pedido['numero_factura']} → "
                f"{ESTADO_ICONO.get(nuevo, nuevo.capitalize())}",
            )
            self.callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


# ====================================================================== #
#  Diálogo: Nueva Venta                                                   #
# ====================================================================== #

class NuevaVentaDialog(tk.Toplevel):

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback      = callback
        self.items_carrito = []
        self.title("Nueva Venta")
        self.geometry("820x620")
        self.resizable(True, True)
        self.grab_set()
        self.configure(bg=COLORS["white"])
        self._build()
        self._cargar_clientes()
        self.focus()

    def _build(self):
        # ── Cliente ─────────────────────────────────────────────────────
        top = tk.Frame(self, bg=COLORS["white"], pady=8)
        top.pack(fill="x", padx=16)
        tk.Label(top, text="Cliente:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.cliente_var = tk.StringVar()
        self.cmb_cliente = ttk.Combobox(top, textvariable=self.cliente_var,
                                        state="readonly", width=30)
        self.cmb_cliente.pack(side="left", padx=8)
        boton(top, "+ Cliente", self._nuevo_cliente, "secondary").pack(side="left")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16)

        centro = tk.Frame(self, bg=COLORS["white"])
        centro.pack(fill="both", expand=True, padx=16, pady=8)

        busq = tk.Frame(centro, bg=COLORS["white"])
        busq.pack(fill="x", pady=(0, 6))
        tk.Label(busq, text="Producto:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.busq_var = tk.StringVar()
        self.busq_entry = tk.Entry(busq, textvariable=self.busq_var,
                                   font=FONTS["normal"], width=22)
        self.busq_entry.pack(side="left", padx=6)
        self.busq_entry.bind("<KeyRelease>", self._buscar_producto)

        self.lista_productos = tk.Listbox(centro, height=6, font=FONTS["small"],
                                          selectmode="single")
        self.lista_productos.pack(fill="x")
        self.lista_productos.bind("<Double-Button-1>", self._seleccionar_producto)
        self._productos_resultado = []

        detalle = tk.Frame(centro, bg=COLORS["white"], pady=4)
        detalle.pack(fill="x")
        tk.Label(detalle, text="Cant:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left")
        self.cant_var = tk.StringVar(value="1")
        tk.Entry(detalle, textvariable=self.cant_var, width=6,
                 font=FONTS["normal"]).pack(side="left", padx=4)
        tk.Label(detalle, text="Precio:", font=FONTS["normal"],
                 bg=COLORS["white"]).pack(side="left", padx=(10, 0))
        self.precio_var = tk.StringVar()
        tk.Entry(detalle, textvariable=self.precio_var, width=10,
                 font=FONTS["normal"]).pack(side="left", padx=4)
        boton(detalle, "➕ Agregar", self._agregar_item, "success").pack(side="left", padx=8)

        ttk.Separator(centro).pack(fill="x", pady=6)

        tk.Label(centro, text="Carrito", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w")
        cols   = ["#", "Código", "Producto", "Cant.", "P.Unit", "Subtotal"]
        anchos = [30, 70, 200, 50, 80, 90]
        self.tabla_carrito = TablaFrame(centro, cols, anchos)
        self.tabla_carrito.pack(fill="both", expand=True)
        boton(centro, "🗑 Quitar ítem", self._quitar_item, "danger").pack(anchor="e", pady=4)

        # ── Panel inferior ───────────────────────────────────────────────
        bot = tk.Frame(self, bg=COLORS["light"], pady=10)
        bot.pack(fill="x", padx=16)

        tk.Label(bot, text="Descuento $:", font=FONTS["normal"],
                 bg=COLORS["light"]).pack(side="left")
        self.desc_var = tk.StringVar(value="0")
        tk.Entry(bot, textvariable=self.desc_var, width=10,
                 font=FONTS["normal"]).pack(side="left", padx=6)

        tk.Label(bot, text="  Estado inicial:", font=FONTS["normal"],
                 bg=COLORS["light"]).pack(side="left", padx=(10, 0))
        self.estado_var = tk.StringVar(value="pendiente")
        ttk.Combobox(bot, textvariable=self.estado_var,
                     values=["pendiente", "despachado"],
                     state="readonly", width=12).pack(side="left", padx=4)

        self.lbl_total = tk.Label(bot, text="Total: $0",
                                  font=FONTS["heading"], bg=COLORS["light"],
                                  fg=COLORS["primary"])
        self.lbl_total.pack(side="right", padx=16)

        self.alerta = AlertaLabel(self)
        self.alerta.pack(padx=16, anchor="w")

        boton(self, "✔ Confirmar Venta", self._confirmar, "success").pack(pady=10)

    def _cargar_clientes(self):
        clientes = PedidoController.listar_clientes()
        self._cliente_map = {c["nombre"]: c["id"] for c in clientes}
        self.cmb_cliente["values"] = list(self._cliente_map.keys())
        if self._cliente_map:
            self.cmb_cliente.current(0)

    def _nuevo_cliente(self):
        nombre = tk.simpledialog.askstring("Nuevo Cliente", "Nombre del cliente:", parent=self)
        if nombre:
            try:
                PedidoController.crear_cliente(nombre)
                self._cargar_clientes()
                self.cmb_cliente.set(nombre)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _buscar_producto(self, event=None):
        termino = self.busq_var.get().strip()
        self.lista_productos.delete(0, "end")
        if not termino or len(termino) < 2:
            return
        self._productos_resultado = ProductoController.buscar_productos(termino)
        for p in self._productos_resultado:
            self.lista_productos.insert(
                "end",
                f"{p['codigo']} — {p['nombre']}  (Stock: {p['stock']}  ${p['precio_venta']:,.0f})"
            )

    def _seleccionar_producto(self, event=None):
        sel = self.lista_productos.curselection()
        if not sel:
            return
        p = self._productos_resultado[sel[0]]
        self._producto_actual = p
        self.precio_var.set(str(p["precio_venta"]))
        self.busq_var.set(f"{p['codigo']} — {p['nombre']}")

    def _agregar_item(self):
        self.alerta.limpiar()
        if not hasattr(self, "_producto_actual"):
            self.alerta.error("Seleccione un producto de la lista.")
            return
        try:
            cantidad = int(self.cant_var.get())
            precio   = float(self.precio_var.get())
        except ValueError:
            self.alerta.error("Cantidad y precio deben ser números.")
            return
        if cantidad <= 0:
            self.alerta.error("La cantidad debe ser mayor a 0.")
            return
        p = self._producto_actual
        self.items_carrito.append({
            "producto_id":     p["id"],
            "codigo":          p["codigo"],
            "nombre":          p["nombre"],
            "cantidad":        cantidad,
            "precio_unitario": precio,
        })
        self._actualizar_carrito()
        del self._producto_actual
        self.busq_var.set("")
        self.cant_var.set("1")
        self.precio_var.set("")
        self.lista_productos.delete(0, "end")

    def _quitar_item(self):
        sel = self.tabla_carrito.tree.selection()
        if not sel:
            return
        self.items_carrito.pop(int(sel[0]))
        self._actualizar_carrito()

    def _actualizar_carrito(self):
        self.tabla_carrito.limpiar()
        subtotal_total = 0
        for i, item in enumerate(self.items_carrito):
            sub = item["cantidad"] * item["precio_unitario"]
            subtotal_total += sub
            self.tabla_carrito.tree.insert("", "end", iid=str(i), values=(
                i + 1, item["codigo"], item["nombre"],
                item["cantidad"], f"${item['precio_unitario']:,.0f}",
                f"${sub:,.0f}",
            ))
        try:
            desc = float(self.desc_var.get() or 0)
        except ValueError:
            desc = 0
        self.lbl_total.config(text=f"Total: ${subtotal_total - desc:,.0f}")

    def _confirmar(self):
        self.alerta.limpiar()
        if not self.items_carrito:
            self.alerta.error("Agregue al menos un producto.")
            return
        try:
            desc       = float(self.desc_var.get() or 0)
            cliente_id = self._cliente_map.get(self.cliente_var.get())
            estado     = self.estado_var.get()
            numero     = PedidoController.crear_pedido(
                cliente_id, self.items_carrito, desc, estado=estado
            )
            texto  = PedidoController.generar_texto_factura(numero)
            padre  = self.master
            self.destroy()
            self.callback()
            FacturaDialog(padre, texto)
        except Exception as e:
            self.alerta.error(str(e))


# ====================================================================== #
#  Diálogo: Factura                                                       #
# ====================================================================== #

class FacturaDialog(tk.Toplevel):

    def __init__(self, parent, texto):
        super().__init__(parent)
        self.title("Factura")
        self.resizable(False, False)
        self.configure(bg=COLORS["white"])
        self.grab_set()

        frame = tk.Frame(self, bg=COLORS["white"])
        frame.pack(padx=16, pady=16)

        txt = tk.Text(frame, font=("Courier", 10), width=52, height=24,
                      bg=COLORS["white"], relief="flat")
        txt.pack()
        txt.insert("end", texto)
        txt.config(state="disabled")

        def copiar():
            self.clipboard_clear()
            self.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Factura copiada al portapapeles.")

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(pady=8)
        boton(btn_frame, "📋 Copiar", copiar, "secondary").pack(side="left", padx=6)
        boton(btn_frame, "✖ Cerrar", self.destroy, "danger").pack(side="left", padx=6)
        self.focus()