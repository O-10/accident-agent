import os
import streamlit as st

GOOGLE_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = "qwen/qwen3.8-27b"
USE_GROQ = True

FREE_PLAN_LIMIT = 5
PREMIUM_PLAN_PRICE = 30.00
PREMIUM_PLAN_NAME = "Premium"

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

if PAYPAL_MODE == "sandbox":
    PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"
else:
    PAYPAL_BASE_URL = "https://api-m.paypal.com"

SECRET_KEY = os.getenv("JWT_SECRET", "accident-agent-secret-key-change-in-production")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@accidentes.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123456")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Administrador")

DB_PATH = os.path.join(os.path.dirname(__file__), "usuarios.db")
