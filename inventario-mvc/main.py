"""
Sistema de Control de Inventario y Rentabilidad
Punto de entrada principal.

Grupo 3 — Nuevas Tecnologías (UTS)
  Jesus Gonzalez | Marlon Gelvez | Sebastian Velandia
"""

import tkinter as tk
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.Models.database import Database
from app.Views.main_window import MainWindow
from config.settings import APP_NAME


def main():
    # Inicializar base de datos
    Database.initialize()

    # Crear ventana principal
    root = tk.Tk()
    app  = MainWindow(root)

    # Centrar ventana
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
