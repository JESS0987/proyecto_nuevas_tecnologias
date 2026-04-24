"""
Views: Componentes reutilizables de la interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk
from config.settings import COLORS, FONTS


# ------------------------------------------------------------------ #
#  Tabla genérica con scrollbar                                        #
# ------------------------------------------------------------------ #

class TablaFrame(tk.Frame):
    """Tabla (Treeview) con barra de desplazamiento vertical y horizontal."""

    def __init__(self, parent, columnas, anchos=None, **kwargs):
        super().__init__(parent, bg=COLORS["white"], **kwargs)
        self.columnas = columnas

        scroll_y = ttk.Scrollbar(self, orient="vertical")
        scroll_x = ttk.Scrollbar(self, orient="horizontal")

        self.tree = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="browse",
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        for i, col in enumerate(columnas):
            ancho = (anchos[i] if anchos else 120)
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=ancho, anchor="center", minwidth=60)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Estilos alternados
        self.tree.tag_configure("par",   background="#F8F9FA")
        self.tree.tag_configure("impar", background=COLORS["white"])
        self.tree.tag_configure("alerta", background="#FDEBD0")

    def limpiar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insertar(self, valores, tag=None, item_id=None):
        kw = {}
        if tag:
            kw["tags"] = (tag,)
        if item_id:
            kw["iid"] = item_id
        idx = len(self.tree.get_children())
        auto_tag = "par" if idx % 2 == 0 else "impar"
        tags = (tag or auto_tag,)
        return self.tree.insert("", "end", values=valores, tags=tags, **{k: v for k, v in kw.items() if k != "tags"})

    def seleccionado(self):
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0])["values"]
        return None

    def seleccionado_id(self):
        sel = self.tree.selection()
        return sel[0] if sel else None


# ------------------------------------------------------------------ #
#  Formulario etiqueta + campo                                         #
# ------------------------------------------------------------------ #

class CampoForm(tk.Frame):
    """Par etiqueta + Entry dentro de un frame."""

    def __init__(self, parent, etiqueta, requerido=False, **kwargs):
        super().__init__(parent, bg=COLORS["white"], **kwargs)
        lbl_text = etiqueta + (" *" if requerido else "")
        tk.Label(
            self, text=lbl_text, font=FONTS["normal"],
            bg=COLORS["white"], fg=COLORS["text_dark"],
            anchor="w", width=16,
        ).pack(side="left")
        self.var    = tk.StringVar()
        self.entry  = tk.Entry(self, textvariable=self.var, font=FONTS["normal"], width=24)
        self.entry.pack(side="left", padx=(4, 0))

    def get(self):
        return self.var.get()

    def set(self, valor):
        self.var.set(valor)

    def clear(self):
        self.var.set("")


# ------------------------------------------------------------------ #
#  Botón estilizado                                                    #
# ------------------------------------------------------------------ #

def boton(parent, texto, comando, color="secondary", **kwargs):
    bg   = COLORS.get(color, COLORS["secondary"])
    btn  = tk.Button(
        parent,
        text=texto,
        command=comando,
        font=FONTS["button"],
        bg=bg, fg=COLORS["white"],
        activebackground=COLORS["primary"],
        activeforeground=COLORS["white"],
        relief="flat", padx=14, pady=6,
        cursor="hand2",
        **kwargs,
    )
    return btn


# ------------------------------------------------------------------ #
#  Barra de búsqueda                                                   #
# ------------------------------------------------------------------ #

class BarraBusqueda(tk.Frame):
    def __init__(self, parent, placeholder="Buscar...", comando=None, **kwargs):
        super().__init__(parent, bg=COLORS["light"], **kwargs)
        tk.Label(self, text="🔍", bg=COLORS["light"], font=FONTS["normal"]).pack(side="left", padx=(8, 2))
        self.var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.var, font=FONTS["normal"], relief="flat", width=30)
        entry.pack(side="left", ipady=4, padx=4)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>",  lambda e: (entry.delete(0, "end") if entry.get() == placeholder else None))
        entry.bind("<FocusOut>", lambda e: (entry.insert(0, placeholder) if not entry.get() else None))
        if comando:
            entry.bind("<KeyRelease>", lambda e: comando(self.var.get()))

    def get(self):
        return self.var.get()


# ------------------------------------------------------------------ #
#  Panel de alertas                                                    #
# ------------------------------------------------------------------ #

class AlertaLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            text="", font=FONTS["small"],
            bg=COLORS["white"], anchor="w",
            **kwargs,
        )

    def error(self, msg):
        self.config(text=f"⚠  {msg}", fg=COLORS["danger"])

    def ok(self, msg):
        self.config(text=f"✔  {msg}", fg=COLORS["success"])

    def limpiar(self):
        self.config(text="")
