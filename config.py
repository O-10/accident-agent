import os

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}

def _get(key, default=""):
    return os.getenv(key, _secrets.get(key, default))

GOOGLE_API_KEY = _get("GOOGLE_GENAI_API_KEY", "")
GROQ_API_KEY = _get("GROQ_API_KEY", "")
MODEL_NAME = "qwen/qwen3.8-27b"
USE_GROQ = True

FREE_PLAN_LIMIT = 5
PREMIUM_PLAN_PRICE = 30.00
PREMIUM_PLAN_NAME = "Premium"

PAYPAL_CLIENT_ID = _get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = _get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = _get("PAYPAL_MODE", "sandbox")

if PAYPAL_MODE == "sandbox":
    PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"
else:
    PAYPAL_BASE_URL = "https://api-m.paypal.com"

SECRET_KEY = _get("JWT_SECRET", "accident-agent-secret-key-change-in-production")

ADMIN_EMAIL = _get("ADMIN_EMAIL", "admin@accidentes.com")
ADMIN_PASSWORD = _get("ADMIN_PASSWORD", "Admin123456")
ADMIN_NAME = _get("ADMIN_NAME", "Administrador")

DB_PATH = os.path.join(os.path.dirname(__file__), "usuarios.db")
