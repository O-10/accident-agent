import streamlit as st
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GROQ_API_KEY, FREE_PLAN_LIMIT, PREMIUM_PLAN_PRICE
from auth import registrar, login, get_current_user
from database import (
    verificar_limite,
    incrementar_uso,
    guardar_investigacion,
    obtener_historial,
)
from payments import crear_suscripcion_paypal, confirmar_pago

st.set_page_config(
    page_title="Agente Investigacion de Accidentes",
    page_icon=":shield:",
    layout="wide",
)


def get_groq_client():
    from groq import Groq
    api_key = GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def chat_with_agent(messages, file_content=""):
    client = get_groq_client()
    if not client:
        return "Error: No hay API key de Groq configurada."

    system_prompt = """Eres un experto en investigacion de accidentes de trabajo (Colombia, Resolucion 1401/2007).

METODOLOGIAS: Ishikawa (6M), 5 Porques, Arbol de Fallas, ECFA, CAPTA, Bow-Tie, TRIZ, FMEA, Bird.

FLUJO: 1) Recopilar datos del accidente 2) Elegir metodologia 3) Analizar causas (inmediatas, basicas, generales, fundamentales) 4) Informe con causa raiz 5) Plan de accion correctiva.

FORMATO INFORME: Datos generales, descripcion, analisis de causas, metodologia, causa raiz, plan de accion (responsable, fecha, recursos), lecciones aprendidas.

Responde en espanol, se tecnico pero claro. Genera tablas y diagramas en texto cuando sea util."""

    groq_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        content = msg["content"]
        if file_content and msg == messages[-1]:
            content = f"{content}\n\n--- CONTENIDO DEL PDF ---\n{file_content}\n--- FIN DEL PDF ---"
        groq_messages.append({"role": msg["role"], "content": content})

    try:
        import time
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=groq_messages,
                    temperature=0.7,
                    max_tokens=4096,
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    return f"Error: {str(e)}"
    except Exception as e:
        return f"Error al conectar con Groq: {str(e)}"


def init_session():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def handle_payment():
    params = st.query_params
    if "payment" in params and params["payment"] == "success":
        order_id = params.get("orderId")
        user = get_current_user()
        if user and order_id:
            if confirmar_pago(user["id"], order_id):
                st.success("Pago exitoso! Ahora tienes plan Premium.")
                st.rerun()
    if "upgrade" in params:
        user = get_current_user()
        if user:
            result = crear_suscripcion_paypal(user["id"], user["email"])
            if result and result.get("approve_url"):
                st.markdown(
                    f'<a href="{result["approve_url"]}" target="_blank">'
                    '<button style="background-color:#0070ba;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-size:16px;">'
                    'Pagar con PayPal - $30/mes</button></a>',
                    unsafe_allow_html=True,
                )


def show_login():
    st.markdown("# :shield: Agente Investigacion de Accidentes")
    st.markdown("### Resolucion 1401 de 2007 - Colombia")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_registro = st.tabs(["Iniciar Sesion", "Registrarse"])

        with tab_login:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Contrasena", type="password", key="login_pass")

            if st.button("Iniciar Sesion", use_container_width=True):
                if email and password:
                    result = login(email, password)
                    if result["success"]:
                        st.session_state.token = result["token"]
                        st.rerun()
                    else:
                        st.error(result["error"])

        with tab_registro:
            nombre = st.text_input("Nombre completo", key="reg_nombre")
            email_reg = st.text_input("Email", key="reg_email")
            pass_reg = st.text_input("Contrasena", type="password", key="reg_pass")
            pass_confirm = st.text_input("Confirmar contrasena", type="password", key="reg_pass2")

            if st.button("Crear Cuenta", use_container_width=True):
                if nombre and email_reg and pass_reg:
                    if pass_reg != pass_confirm:
                        st.error("Las contrasenas no coinciden")
                    elif len(pass_reg) < 6:
                        st.error("La contrasena debe tener al menos 6 caracteres")
                    else:
                        result = registrar(email_reg, pass_reg, nombre)
                        if result["success"]:
                            st.session_state.token = result["token"]
                            st.success("Cuenta creada exitosamente")
                            st.rerun()
                        else:
                            st.error(result["error"])


def show_chat():
    user = get_current_user()
    if not user:
        st.rerun()
        return

    with st.sidebar:
        st.markdown(f"**Hola, {user['nombre']}**")
        plan_color = "🟢" if user["plan"] == "premium" else "🟡"
        st.markdown(f"{plan_color} Plan: **{user['plan'].upper()}**")

        if user["plan"] == "gratis":
            usos_restantes = FREE_PLAN_LIMIT - user["investigaciones_usadas"]
            st.markdown(f"Investigaciones restantes: **{usos_restantes}/{FREE_PLAN_LIMIT}**")
            if usos_restantes <= 0:
                st.warning("Has agotado tus investigaciones gratuitas")
                st.markdown(
                    f'<a href="?upgrade={user["id"]}" target="_self">'
                    '<button style="background-color:#0070ba;color:white;width:100%;padding:8px;border:none;border-radius:5px;cursor:pointer;">'
                    'Actualizar a Premium - $30/mes</button></a>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("Investigaciones: **Ilimitadas**")

        st.markdown("---")
        st.markdown("Powered by **Groq + Qwen 3.8** (gratis)")

        if st.button("Cerrar Sesion"):
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("## :shield: Investigador de Accidentes de Trabajo")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Describe el accidente de trabajo a investigar..."):
        user = get_current_user()
        if not user:
            st.rerun()
            return

        if user["plan"] == "gratis" and user["investigaciones_usadas"] >= FREE_PLAN_LIMIT:
            st.error("Has agotado tus investigaciones gratuitas. Actualiza a Premium.")
            st.rerun()
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        uploaded_file = st.file_uploader(
            "Subir reporte PDF (opcional)",
            type=["pdf"],
            key="file_uploader",
        )

        file_content = ""
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                import pdfplumber
                with pdfplumber.open(tmp_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            file_content += text + "\n"
                st.success(f"PDF cargado: {len(file_content)} caracteres extraidos")
            except Exception as e:
                st.error(f"Error al leer PDF: {e}")
            finally:
                os.unlink(tmp_path)

        with st.chat_message("assistant"):
            with st.spinner("Analizando accidente con Qwen 3.8..."):
                response_text = chat_with_agent(st.session_state.messages, file_content)

                if response_text:
                    st.markdown(response_text)
                else:
                    st.markdown("El agente proceso tu solicitud. Intenta de nuevo.")

        if response_text:
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            incrementar_uso(user["id"])
            guardar_investigacion(user["id"], prompt[:100], prompt, response_text)


def show_historial():
    user = get_current_user()
    if not user:
        st.rerun()
        return

    with st.sidebar:
        st.markdown(f"**Hola, {user['nombre']}**")
        if st.button("Volver al Chat"):
            st.rerun()
        if st.button("Cerrar Sesion"):
            st.session_state.token = None
            st.rerun()

    st.markdown("## :clipboard: Historial de Investigaciones")

    historial = obtener_historial(user["id"])

    if not historial:
        st.info("No tienes investigaciones aun.")
    else:
        for inv in historial:
            with st.expander(f"**{inv['titulo']}** - {inv['fecha']}"):
                st.markdown("**Diagnostico:**")
                st.markdown(inv["diagnostico"])


def main():
    init_session()
    handle_payment()

    if st.session_state.token:
        user = get_current_user()
        if not user:
            st.session_state.token = None
            st.rerun()
            return

        tab = st.sidebar.selectbox("Navegacion", ["Chat", "Historial"])

        if tab == "Chat":
            show_chat()
        elif tab == "Historial":
            show_historial()
    else:
        show_login()


if __name__ == "__main__":
    main()
