"""
Model: Conexión dual — SQLite (escritura) + MongoDB (tiempo real)
"""

import sqlite3
import os
import hashlib
from contextlib import contextmanager
from datetime import datetime, timezone

from config.settings import DATABASE_PATH, DATABASE_SQL

# ── Configuración Mongo ────────────────────────────────────────────────────
_MONGO_URI     = os.environ.get("MONGO_URI",     "mongodb://localhost:27017")
_MONGO_DB      = os.environ.get("MONGO_DB",      "glamour_inventario")
_MONGO_ENABLED = os.environ.get("MONGO_ENABLED", "1") == "1"

_mongo_client = None
_mongo_db     = None


def get_mongo():
    global _mongo_client, _mongo_db, _MONGO_ENABLED
    if not _MONGO_ENABLED:
        return None, None
    if _mongo_db is not None:
        return _mongo_client, _mongo_db
    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(_MONGO_URI, serverSelectionTimeoutMS=3000)
        _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client[_MONGO_DB]
        print(f"[Mongo] Conectado a {_MONGO_DB}")
        _crear_indices(_mongo_db)
    except Exception as e:
        print(f"[Mongo] Sin conexion ({e}). Mongo desactivado.")
        _MONGO_ENABLED = False
        _mongo_client  = None
        _mongo_db      = None
    return _mongo_client, _mongo_db


def _crear_indices(db):
    try:
        from pymongo import ASCENDING
        db.pedidos.create_index("numero_factura",   unique=True, background=True)
        db.pedidos.create_index("estado",            background=True)
        db.pedidos.create_index([("fecha", ASCENDING)], background=True)
        db.pedidos.create_index("ultima_actualizacion", background=True)
        db.productos.create_index("codigo", unique=True, background=True)
        db.productos.create_index("inventario.stock_bajo", background=True)
    except Exception:
        pass


def mongo_upsert_pedido(pedido_doc: dict):
    _, db = get_mongo()
    if db is None:
        return
    try:
        pedido_doc["ultima_actualizacion"] = datetime.now(timezone.utc)
        db.pedidos.update_one(
            {"numero_factura": pedido_doc["numero_factura"]},
            {"$set": pedido_doc},
            upsert=True,
        )
    except Exception as e:
        print(f"[Mongo] upsert_pedido error: {e}")


def mongo_upsert_producto(producto_doc: dict):
    _, db = get_mongo()
    if db is None:
        return
    try:
        db.productos.update_one(
            {"codigo": producto_doc["codigo"]},
            {"$set": producto_doc},
            upsert=True,
        )
    except Exception as e:
        print(f"[Mongo] upsert_producto error: {e}")


class Database:

    @classmethod
    @contextmanager
    def get_connection(cls):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def _get_sql_hash(cls):
        with open(DATABASE_SQL, "r", encoding="utf-8") as f:
            return hashlib.md5(f.read().encode()).hexdigest()

    @classmethod
    def initialize(cls):
        hash_path   = DATABASE_PATH + ".hash"
        sql_hash    = cls._get_sql_hash()
        sql_changed = True

        if os.path.exists(hash_path):
            with open(hash_path, "r") as f:
                sql_changed = f.read().strip() != sql_hash

        if sql_changed or not os.path.exists(DATABASE_PATH):
            if os.path.exists(DATABASE_PATH):
                os.remove(DATABASE_PATH)
                print("[DB] SQL cambio — base de datos recreada.")
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            with open(DATABASE_SQL, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.close()
            with open(hash_path, "w") as f:
                f.write(sql_hash)
            print("[DB] Base de datos inicializada correctamente.")
        else:
            print("[DB] Sin cambios en SQL — datos existentes conservados.")

        import threading
        threading.Thread(target=cls._sync_inicial, daemon=True).start()

    @classmethod
    def _sync_inicial(cls):
        _, db = get_mongo()
        if db is None:
            return
        try:
            from app.Models.producto_model import ProductoModel
            from app.Models.pedido_model   import PedidoModel

            productos = ProductoModel.obtener_todos(solo_activos=False)
            for p in productos:
                mongo_upsert_producto(_producto_a_doc(dict(p)))

            pedidos = PedidoModel.obtener_todos(limite=9999)
            for p in pedidos:
                pd = dict(p)
                _, items = PedidoModel.obtener_por_id(pd["id"])
                mongo_upsert_pedido(_pedido_a_doc(pd, [dict(i) for i in items]))

            print(f"[Mongo] Sync inicial: {len(productos)} productos, {len(pedidos)} pedidos")
        except Exception as e:
            print(f"[Mongo] Sync inicial error: {e}")


def _ts(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor))
    except Exception:
        return valor


def _producto_a_doc(p: dict) -> dict:
    costo  = p.get("costo",        0) or 0
    pventa = p.get("precio_venta", 0) or 0
    stock  = p.get("stock",        0) or 0
    smin   = p.get("stock_minimo", 5) or 5
    return {
        "codigo":      p.get("codigo"),
        "nombre":      p.get("nombre"),
        "descripcion": p.get("descripcion"),
        "categoria": {
            "id":     p.get("categoria_id"),
            "nombre": p.get("categoria_nombre"),
        },
        "precios": {
            "costo":        costo,
            "precio_venta": pventa,
            "margen_pct":   round(((pventa - costo) / costo * 100) if costo else 0, 1),
        },
        "inventario": {
            "stock":        stock,
            "stock_minimo": smin,
            "stock_bajo":   stock <= smin,
        },
        "activo":         bool(p.get("activo", 1)),
        "creado_en":      _ts(p.get("creado_en")),
        "actualizado_en": _ts(p.get("actualizado_en")),
    }


def _pedido_a_doc(p: dict, items: list) -> dict:
    subtotal = p.get("subtotal", 0) or 0
    ganancia = sum(
        (i.get("precio_unitario", 0) - i.get("costo_unitario", 0)) * i.get("cantidad", 0)
        for i in items
    )
    items_doc = [{
        "producto_id":     i.get("producto_id"),
        "producto_nombre": i.get("producto_nombre"),
        "producto_codigo": i.get("codigo") or i.get("producto_codigo"),
        "cantidad":        i.get("cantidad"),
        "precio_unitario": i.get("precio_unitario"),
        "costo_unitario":  i.get("costo_unitario"),
        "subtotal":        i.get("subtotal"),
        "ganancia_item":   round(
            (i.get("precio_unitario", 0) - i.get("costo_unitario", 0))
            * i.get("cantidad", 0), 2
        ),
    } for i in items]

    return {
        "numero_factura": p.get("numero_factura"),
        "cliente": {
            "id":        p.get("cliente_id"),
            "nombre":    p.get("cliente_nombre"),
            "documento": p.get("documento") or p.get("cliente_doc"),
        },
        "fecha": _ts(p.get("fecha")),
        "financiero": {
            "subtotal":      subtotal,
            "descuento":     p.get("descuento", 0),
            "total":         p.get("total", 0),
            "ganancia_neta": round(ganancia, 2),
            "margen_pct":    round((ganancia / subtotal * 100) if subtotal else 0, 1),
        },
        "estado":    p.get("estado"),
        "notas":     p.get("notas"),
        "items":     items_doc,
        "num_items": len(items_doc),
    }