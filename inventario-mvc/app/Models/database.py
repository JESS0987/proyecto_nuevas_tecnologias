"""
Model: Conexión a la base de datos SQLite
"""

import sqlite3
import os
import hashlib
from contextlib import contextmanager
from config.settings import DATABASE_PATH, DATABASE_SQL


class Database:

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager que abre la conexión, hace commit al salir
        sin error, o rollback si hay excepción.

        Uso:
            with Database.get_connection() as conn:
                conn.execute(...)
            # commit automático al salir del with
        """
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        # isolation_level por defecto ('') activa transacciones implícitas
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
        """Calcula el hash del archivo SQL actual."""
        with open(DATABASE_SQL, "r", encoding="utf-8") as f:
            return hashlib.md5(f.read().encode()).hexdigest()

    @classmethod
    def initialize(cls):
        """
        Recrea la base de datos SOLO si el SQL cambió.
        Si no cambió, conserva todos los datos existentes.
        """
        hash_path   = DATABASE_PATH + ".hash"
        sql_hash    = cls._get_sql_hash()
        sql_changed = True

        if os.path.exists(hash_path):
            with open(hash_path, "r") as f:
                sql_changed = f.read().strip() != sql_hash

        if sql_changed or not os.path.exists(DATABASE_PATH):
            if os.path.exists(DATABASE_PATH):
                os.remove(DATABASE_PATH)
                print("[DB] SQL cambió — base de datos recreada.")
            # Para executescript usamos conexión directa (no el context manager)
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