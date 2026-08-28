"""Runner ADK completo para la app Streamlit.

Ejecuta el agente de investigacion de accidentes usando el ADK con Runner,
sesiones, herramientas y callbacks, pero sobre Groq via LiteLLM (en lugar
del Gemini que usa el agente local). No modifica agent.py ni tools.py.
"""

import asyncio
import logging
import threading
import time

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# Reutiliza las herramientas del agente local
from tools import tools

logging.basicConfig(level=logging.WARNING)

MODEL_GROQ = "groq/qwen/qwen3.8-27b"
APP_NAME = "accident_investigation_agent"
USER_ID = "streamlit_user"

_runner = None
_session_service = None
_created_sessions = set()

# Instruccion compacta (el knowledge base completo excede el TPM gratuito de Groq).
COMPACT_INSTRUCTION = """Eres un Agente Experto en Investigacion de Accidentes de Trabajo (Resolucion 1401 de 2007 - Colombia).

METODOLOGIAS disponibles:
- Ishikawa (6M): causa-efecto con categorias Mano de obra, Metodos, Maquinaria, Materiales, Medio ambiente, Administracion
- 5 Porques: profundizar hasta la causa raiz (minimo 3 niveles)
- Arbol de Fallas (FTA): modelar fallas con compuertas AND/OR
- ECFA: secuencia temporal de eventos
- CAPTA: reportes para la ARL (Ministerio del Trabajo Colombia)
- Analisis de Cambios: antes vs despues del evento
- Bow-Tie: amenazas, controles preventivos y mitigantes
- TRIZ, FMEA, Bird: analisis avanzados

FLUJO DE INVESTIGACION:
FASE 1 - Recopilar: fecha, lugar, descripcion del evento, tipo de accidente, consecuencias, EPP usado, condiciones del lugar.
FASE 2 - Seleccionar metodologia segun el caso (usa herramientas para generar diagramas cuando aplique).
FASE 3 - Aplicar la metodologia paso a paso con preguntas al usuario.
FASE 4 - Generar informe: 1) datos generales 2) descripcion 3) analisis de causas (inmediatas, basicas, generales, fundamentales) 4) metodologia aplicada 5) causa raiz 6) plan de accion correctiva con responsables, fechas y recursos 7) cumplimiento Resolucion 1401 8) lecciones aprendidas.
FASE 5 - Plan de accion: accion correctiva, responsable, fecha, recursos, seguimiento.

CAUSAS (Resolucion 1401):
- Inmediatas: actos y condiciones inseguras
- Basicas: administracion deficiente de seguridad, falta de conocimiento, factores personales
- Generales: liderazgo/supervision, ingenieria, mantenimiento, carga de trabajo
- Fundamentales: gerencia y control inadecuado, practicas sub-estandar

REGLAS: menciona la Resolucion 1401 cuando aplique; lenguaje tecnico pero claro; genera tablas y diagramas (Mermaid) cuando sea util; prioriza seguridad y prevencion; incluye lecciones aprendidas.
Responde en espanol."""


def _build_instruction():
    return COMPACT_INSTRUCTION


def _before_agent_callback(callback_context=None):
    print("[ADK] Iniciando ejecucion del agente")
    return None


def _after_agent_callback(callback_context=None):
    print("[ADK] Finalizo la ejecucion del agente")
    return None


def _get_runner():
    """Construye (una sola vez) el runner ADK con session service y callbacks."""
    global _runner, _session_service

    if _runner is not None:
        return _runner

    # LiteLLM lee las API keys desde variables de entorno. Asegura que Groq
    # este disponible tanto localmente (.env) como en Streamlit Cloud (secrets).
    import os
    from config import GROQ_API_KEY
    if GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY

    agent = Agent(
        name="accident_investigation_agent",
        model=LiteLlm(model=MODEL_GROQ),
        description=(
            "Experto en investigacion de accidentes de trabajo y cumplimiento "
            "de la Resolucion 1401 de 2007"
        ),
        instruction=_build_instruction(),
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4096,
        ),
        tools=tools,
        before_agent_callback=_before_agent_callback,
        after_agent_callback=_after_agent_callback,
    )

    _session_service = InMemorySessionService()
    _runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=_session_service,
    )
    return _runner


def _ensure_session(runner, session_id):
    """Crea la sesion ADK si aun no existe para ese session_id."""
    global _session_service, _created_sessions
    if session_id in _created_sessions:
        return
    _call_async_return(
        _session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    )
    _created_sessions.add(session_id)


def _call_async_return(coro):
    """Ejecuta un coroutine que produce un valor, de forma segura.

    Fuera de un event loop usa asyncio.run; si ya hay un loop activo (Streamlit),
    ejecuta en un hilo con su propio event loop para no interferir.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        return asyncio.run(coro)

    result = {}

    def _worker():
        loop2 = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop2)
            result["value"] = loop2.run_until_complete(coro)
        finally:
            loop2.close()

    thread = threading.Thread(target=_worker)
    thread.start()
    thread.join(timeout=240)
    return result.get("value")



def _to_content(message):
    role = "model" if message.get("role") == "assistant" else "user"
    return types.Content(
        role=role,
        parts=[types.Part.from_text(text=message.get("content", ""))],
    )


def run_adk_agent(messages, file_content="", session_id="accident_workspace"):
    """Ejecuta el agente ADK completo sobre Groq y devuelve la respuesta final.

    Args:
        messages: historial de la conversacion [{"role", "content"}, ...]
        file_content: contenido de un PDF adjunto (opcional)
        session_id: identificador unico de conversacion por usuario
    """
    runner = _get_runner()
    _ensure_session(runner, session_id)

    content_messages = []
    for msg in messages:
        content = msg.get("content", "")
        if file_content and msg is messages[-1]:
            content = (
                f"{content}\n\n--- CONTENIDO DEL PDF ---\n{file_content}\n--- FIN DEL PDF ---"
            )
        content_messages.append(_to_content({**msg, "content": content}))

    if not content_messages:
        content_messages.append(
            types.Content(role="user", parts=[types.Part.from_text(text="Hola")])
        )

    async def _run():
        final_text = None
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=content_messages[-1],
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_text = "".join(
                        p.text or "" for p in event.content.parts if hasattr(p, "text")
                    )
        return final_text

    try:
        for attempt in range(3):
            try:
                return _call_async_return(_run())
            except Exception as e:
                err = str(e)
                is_rate = "429" in err or "rate_limit" in err.lower() or "ratelimiterror" in err.lower()
                if is_rate and attempt < 2:
                    time.sleep(8 * (attempt + 1))
                else:
                    return f"Error al ejecutar el agente ADK: {err}"
        return None
    except Exception as e:
        return f"Error al ejecutar el agente ADK: {str(e)}"
