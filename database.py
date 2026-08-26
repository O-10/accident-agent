import sqlite3
import os
from datetime import datetime
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            plan TEXT DEFAULT 'gratis',
            investigaciones_usadas INTEGER DEFAULT 0,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            paypal_subscription_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT,
            contenido TEXT,
            diagnostico TEXT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            monto REAL,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'pendiente',
            paypal_order_id TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


def crear_usuario(email, password_hash, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (email, password_hash, nombre) VALUES (?, ?, ?)",
            (email, password_hash, nombre),
        )
        conn.commit()
        usuario_id = cursor.lastrowid
        return usuario_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def obtener_usuario_por_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def obtener_usuario_por_id(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def verificar_limite(usuario_id):
    usuario = obtener_usuario_por_id(usuario_id)
    if not usuario:
        return False
    if usuario["plan"] == "premium":
        return True
    from config import FREE_PLAN_LIMIT
    return usuario["investigaciones_usadas"] < FREE_PLAN_LIMIT


def incrementar_uso(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET investigaciones_usadas = investigaciones_usadas + 1 WHERE id = ?",
        (usuario_id,),
    )
    conn.commit()
    conn.close()


def actualizar_plan(usuario_id, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET plan = ?, investigaciones_usadas = 0 WHERE id = ?",
        (plan, usuario_id),
    )
    conn.commit()
    conn.close()


def guardar_investigacion(usuario_id, titulo, contenido, diagnostico):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigaciones (usuario_id, titulo, contenido, diagnostico) VALUES (?, ?, ?, ?)",
        (usuario_id, titulo, contenido, diagnostico),
    )
    conn.commit()
    investigacion_id = cursor.lastrowid
    conn.close()
    return investigacion_id


def obtener_historial(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM investigaciones WHERE usuario_id = ? ORDER BY fecha DESC",
        (usuario_id,),
    )
    historial = cursor.fetchall()
    conn.close()
    return historial


def guardar_pago(usuario_id, monto, paypal_order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pagos (usuario_id, monto, paypal_order_id, estado) VALUES (?, ?, ?, 'completado')",
        (usuario_id, monto, paypal_order_id),
    )
    conn.commit()
    conn.close()


def actualizar_paypal_subscription(usuario_id, subscription_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET paypal_subscription_id = ? WHERE id = ?",
        (subscription_id, usuario_id),
    )
    conn.commit()
    conn.close()


def crear_usuario_admin():
    from config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME
    import bcrypt

    usuario = obtener_usuario_por_email(ADMIN_EMAIL)
    if usuario:
        return usuario["id"]

    password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (email, password_hash, nombre, plan) VALUES (?, ?, ?, 'premium')",
        (ADMIN_EMAIL, password_hash, ADMIN_NAME),
    )
    conn.commit()
    admin_id = cursor.lastrowid
    conn.close()
    return admin_id


init_db()
crear_usuario_admin()
