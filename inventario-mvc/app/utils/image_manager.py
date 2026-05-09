"""
Utilidad: Gestión de imágenes de productos
Las imágenes se guardan en: assets/productos/<codigo>.png (o .jpg, .jpeg, .webp)
No requiere cambios en la BD ni en la API.
"""

import os
from pathlib import Path

# Carpeta donde se guardan las imágenes
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets" / "productos"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

EXTENSIONES = [".png", ".jpg", ".jpeg", ".webp", ".gif"]

_cache = {}  # cache de PhotoImage para evitar garbage collection


def ruta_imagen(codigo: str) -> Path | None:
    """Busca la imagen del producto por su código. Retorna Path o None."""
    for ext in EXTENSIONES:
        ruta = ASSETS_DIR / f"{codigo}{ext}"
        if ruta.exists():
            return ruta
    return None


def cargar_thumbnail(codigo: str, size=(60, 60)):
    """
    Carga la imagen del producto como PhotoImage de Tkinter.
    Requiere Pillow (pip install Pillow).
    Retorna PhotoImage o None si no hay imagen.
    """
    ruta = ruta_imagen(codigo)
    if ruta is None:
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(ruta).convert("RGBA")
        img.thumbnail(size, Image.LANCZOS)
        # Fondo blanco para imágenes con transparencia
        fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
        fondo.paste(img, mask=img.split()[3])
        photo = ImageTk.PhotoImage(fondo.convert("RGB"))
        _cache[codigo] = photo  # evitar garbage collection
        return photo
    except ImportError:
        print("[ImageManager] Pillow no instalado. Ejecuta: pip install Pillow")
        return None
    except Exception as e:
        print(f"[ImageManager] Error cargando imagen de {codigo}: {e}")
        return None


def guardar_imagen(codigo: str, ruta_origen: str) -> bool:
    """
    Copia la imagen seleccionada por el usuario a la carpeta assets/productos/.
    La guarda como <codigo>.png
    """
    try:
        from PIL import Image
        img = Image.open(ruta_origen).convert("RGB")
        destino = ASSETS_DIR / f"{codigo}.png"
        img.save(destino, "PNG")
        # Limpiar caché para recargar
        _cache.pop(codigo, None)
        return True
    except ImportError:
        print("[ImageManager] Pillow no instalado. Ejecuta: pip install Pillow")
        return False
    except Exception as e:
        print(f"[ImageManager] Error guardando imagen: {e}")
        return False


def eliminar_imagen(codigo: str):
    """Elimina la imagen guardada para ese código."""
    for ext in EXTENSIONES:
        ruta = ASSETS_DIR / f"{codigo}{ext}"
        if ruta.exists():
            ruta.unlink()
    _cache.pop(codigo, None)
