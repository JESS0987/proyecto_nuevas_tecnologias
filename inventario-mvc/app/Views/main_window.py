"""
View: Ventana Principal (Application Shell)
"""

import tkinter as tk
from tkinter import ttk
from app.Views.productos_view  import ProductosView
from app.Views.ventas_view     import VentasView
from app.Views.rentabilidad_view import RentabilidadView
from config.settings import COLORS, FONTS, APP_NAME, APP_VERSION, APP_TEAM


class MainWindow:

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1100x680")
        self.root.minsize(900, 560)
        self.root.configure(bg=COLORS["primary"])
        self._build()

    def _build(self):
        # ── Sidebar ─────────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=COLORS["primary"], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="📋\nInventario\nPro",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["primary"], fg=COLORS["white"],
            pady=20, justify="center",
        ).pack(fill="x")
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=12)

        self.pagina_actual = None
        self.botones_nav   = {}

        nav_items = [
            ("📦  Inventario",     "inventario"),
            ("🛒  Ventas",         "ventas"),
            ("📊  Rentabilidad",   "rentabilidad"),
        ]
        for texto, key in nav_items:
            btn = tk.Button(
                sidebar, text=texto,
                font=FONTS["normal"],
                bg=COLORS["primary"], fg=COLORS["white"],
                activebackground=COLORS["secondary"],
                activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=16, pady=12,
                cursor="hand2",
                command=lambda k=key: self._navegar(k),
            )
            btn.pack(fill="x")
            self.botones_nav[key] = btn

        # Versión abajo
        tk.Label(
            sidebar,
            text=f"\nv{APP_VERSION}\n{APP_TEAM}",
            font=FONTS["small"],
            bg=COLORS["primary"], fg=COLORS["text_light"],
            wraplength=160, justify="center",
        ).pack(side="bottom", pady=12)

        # ── Contenido ────────────────────────────────────────────────────
        self.content = tk.Frame(self.root, bg=COLORS["light"])
        self.content.pack(side="left", fill="both", expand=True)

        # Vista inicial
        self._navegar("inventario")

    def _navegar(self, pagina):
        # Resaltar botón activo
        for key, btn in self.botones_nav.items():
            btn.config(
                bg=COLORS["secondary"] if key == pagina else COLORS["primary"]
            )

        # Limpiar contenido
        for w in self.content.winfo_children():
            w.destroy()

        # Instanciar vista
        if pagina == "inventario":
            vista = ProductosView(self.content)
        elif pagina == "ventas":
            vista = VentasView(self.content)
        elif pagina == "rentabilidad":
            vista = RentabilidadView(self.content)
        else:
            return

        vista.pack(fill="both", expand=True)
        self.pagina_actual = pagina
