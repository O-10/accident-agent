import bcrypt
import jwt
import streamlit as st
from datetime import datetime, timedelta
from database import crear_usuario, obtener_usuario_por_email
from config import SECRET_KEY


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def crear_token(usuario_id):
    payload = {
        "usuario_id": usuario_id,
        "exp": datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verificar_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["usuario_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def registrar(email, password, nombre):
    password_hash = hash_password(password)
    usuario_id = crear_usuario(email, password_hash, nombre)
    if usuario_id:
        token = crear_token(usuario_id)
        return {"success": True, "usuario_id": usuario_id, "token": token}
    return {"success": False, "error": "El email ya está registrado"}


def login(email, password):
    usuario = obtener_usuario_por_email(email)
    if usuario and verificar_password(password, usuario["password_hash"]):
        token = crear_token(usuario["id"])
        return {"success": True, "usuario_id": usuario["id"], "token": token}
    return {"success": False, "error": "Email o contraseña incorrectos"}


def get_current_user():
    token = st.session_state.get("token")
    if token:
        usuario_id = verificar_token(token)
        if usuario_id:
            from database import obtener_usuario_por_id
            return obtener_usuario_por_id(usuario_id)
    return None


def require_login():
    user = get_current_user()
    if not user:
        st.stop()
    return user
