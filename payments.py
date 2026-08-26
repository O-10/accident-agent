import requests
import streamlit as st
from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_BASE_URL, PREMIUM_PLAN_PRICE
from database import guardar_pago, actualizar_plan, actualizar_paypal_subscription


def get_access_token():
    auth = (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    resp = requests.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", auth=auth, data=data)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None


def crear_suscripcion_paypal(usuario_id, email_usuario):
    access_token = get_access_token()
    if not access_token:
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": f"INV-{usuario_id}",
                "description": "Suscripcion Premium - Agente Investigacion Accidentes",
                "amount": {
                    "currency_code": "USD",
                    "value": str(PREMIUM_PLAN_PRICE),
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": str(PREMIUM_PLAN_PRICE),
                        }
                    },
                },
                "items": [
                    {
                        "name": "Plan Premium",
                        "description": "Investigaciones ilimitadas por 1 mes",
                        "unit_amount": {
                            "currency_code": "USD",
                            "value": str(PREMIUM_PLAN_PRICE),
                        },
                        "quantity": "1",
                    }
                ],
            }
        ],
        "application_context": {
            "brand_name": "Agente Investigacion Accidentes",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW",
            "return_url": "http://localhost:8501?payment=success",
            "cancel_url": "http://localhost:8501?payment=cancelled",
        },
    }

    resp = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        json=payload,
        headers=headers,
    )

    if resp.status_code == 201:
        data = resp.json()
        order_id = data.get("id")
        approve_link = None
        for link in data.get("links", []):
            if link.get("rel") == "approve":
                approve_link = link.get("href")
        return {"order_id": order_id, "approve_url": approve_link}

    return None


def confirmar_pago(usuario_id, order_id):
    access_token = get_access_token()
    if not access_token:
        return False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
        headers=headers,
    )

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "COMPLETED":
            guardar_pago(usuario_id, PREMIUM_PLAN_PRICE, order_id)
            actualizar_plan(usuario_id, "premium")
            return True

    return False


def get_paypal_button_html(usuario_id):
    return f"""
    <form action="http://localhost:8501" method="get">
        <input type="hidden" name="upgrade" value="{usuario_id}">
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_subscribe_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!">
    </form>
    """
