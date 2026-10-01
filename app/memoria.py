"""Gestión de memoria corta de la conversación."""

def agregar(historial: list[dict], rol: str, texto: str) -> None:
    """Añade un mensaje al historial. Roles: 'usuario', 'modelo'."""
    historial.append({"rol": rol, "texto": texto})

def recortar(historial: list[dict], max_mensajes: int) -> list[dict]:
    """
    Devuelve una copia con los últimos max_mensajes sin modificar el historial original.
    Si el primer mensaje resultante es del modelo, se descarta.
    """
    if max_mensajes <= 0 or not historial:
        return []
    recorte = list(historial[-max_mensajes:])
    
    if recorte and recorte[0].get("rol") == "modelo":
        recorte = recorte[1:]
    return recorte