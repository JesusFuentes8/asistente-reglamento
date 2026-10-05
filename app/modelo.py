"""Único punto de conexión con la API de Google Gemini (google-genai)."""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_cliente = None

def _obtener_cliente():
    global _cliente
    if _cliente is None:
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not key:
            raise ValueError("GEMINI_API_KEY no configurada en las variables de entorno.")

        # Inicialización oficial estándar de la Gemini Developer API (gratuita)
        _cliente = genai.Client(
            api_key=key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=5,
                    initial_delay=2.0,
                    max_delay=30.0
                )
            )
        )
    return _cliente

def llamar_modelo(historial: list[dict], sistema: str) -> dict:
    cliente = _obtener_cliente()
    modelo_nombre = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    contents = []
    for m in historial:
        rol_sdk = "user" if m.get("rol") == "usuario" else "model"
        contents.append(
            types.Content(
                role=rol_sdk,
                parts=[types.Part(text=m.get("texto", ""))]
            )
        )

    config = types.GenerateContentConfig(
        system_instruction=sistema,
        # Desactiva la llamada automática a funciones para evitar advertencias de consola
        tools=None
    )

    respuesta = _cliente.models.generate_content(
        model=modelo_nombre,
        contents=contents,
        config=config
    )

    texto_resp = respuesta.text or ""
    uso = respuesta.usage_metadata

    tokens_in = uso.prompt_token_count if uso and uso.prompt_token_count else 0
    tokens_out = (
        (uso.candidates_token_count or 0) + (uso.thoughts_token_count or 0)
        if uso else 0
    )

    return {
        "texto": texto_resp,
        "tokens_entrada": tokens_in,
        "tokens_salida": tokens_out,
        "modelo": modelo_nombre
    }