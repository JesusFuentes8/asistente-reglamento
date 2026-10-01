"""Único punto de conexión con la API de Google Gemini (google-genai)."""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Cliente inicializado una sola vez con opciones de reintento
_api_key = os.environ.get("GEMINI_API_KEY", "")
_cliente = None

if _api_key:
    _cliente = genai.Client(
        api_key=_api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=5,
                initial_delay=2.0,
                max_delay=30.0
            )
        )
    )

def llamar_modelo(historial: list[dict], sistema: str) -> dict:
    """
    Realiza la llamada al modelo Gemini a partir del historial recortado.
    Devuelve un diccionario con texto, tokens_entrada, tokens_salida y modelo.
    """
    global _cliente
    if _cliente is None:
        _api_key_actual = os.environ.get("GEMINI_API_KEY", "")
        if not _api_key_actual:
            raise ValueError("GEMINI_API_KEY no configurada en las variables de entorno.")
        _cliente = genai.Client(
            api_key=_api_key_actual,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=5,
                    initial_delay=2.0,
                    max_delay=30.0
                )
            )
        )

    modelo_nombre = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

    contents = []
    for m in historial:
        rol_sdk = "user" if m.get("rol") == "usuario" else "model"
        contents.append(
            types.Content(
                role=rol_sdk,
                parts=[types.Part(text=m.get("texto", ""))]
            )
        )

    config = types.GenerateContentConfig(system_instruction=sistema)

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