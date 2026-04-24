"""
Configuración global del sistema
Sistema de Control de Inventario y Rentabilidad
"""

import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base de datos
DATABASE_PATH = os.path.join(BASE_DIR, "inventario.db")
DATABASE_SQL  = os.path.join(BASE_DIR, "database.sql")

# Reportes
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Configuración de la aplicación
APP_NAME    = "Sistema de Inventario y Rentabilidad"
APP_VERSION = "1.0.0"
APP_TEAM    = "Jesus Gonzalez, Marlon Gelvez, Sebastian Velandia"

# Stock mínimo por defecto
DEFAULT_STOCK_MINIMO = 5

# Colores de la interfaz
COLORS = {
    "primary":    "#2C3E50",
    "secondary":  "#3498DB",
    "success":    "#27AE60",
    "warning":    "#F39C12",
    "danger":     "#E74C3C",
    "light":      "#ECF0F1",
    "white":      "#FFFFFF",
    "text_dark":  "#2C3E50",
    "text_light": "#7F8C8D",
}

# Fuentes
FONTS = {
    "title":   ("Helvetica", 16, "bold"),
    "heading": ("Helvetica", 13, "bold"),
    "normal":  ("Helvetica", 11),
    "small":   ("Helvetica", 9),
    "button":  ("Helvetica", 11, "bold"),
}
