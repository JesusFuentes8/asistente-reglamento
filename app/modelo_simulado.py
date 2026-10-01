"""Modelo falso con guion cíclico de tres respuestas para pruebas locales sin red."""

_contador = 0

GUION = [
    {
        "texto": "Respuesta: Debes portar de manera visible la credencial del TecNM para identificarte y realizar trámites.\nFundamento: Art. 7, fracc. XV\nConfianza: alta",
        "tokens_entrada": 6400,
        "tokens_salida": 75,
        "modelo": "simulado"
    },
    {
        "texto": "Respuesta: El tema no se encuentra contemplado en la normativa de convivencia estudiantil.\nFundamento: no consta en el Reglamento de Estudiantes\nConfianza: alta",
        "tokens_entrada": 6450,
        "tokens_salida": 60,
        "modelo": "simulado"
    },
    {
        "texto": "Respuesta: La sanción indicada se encuentra regulada en el apartado correspondiente.\nFundamento: Art. 31, fracc. II\nConfianza: media",
        "tokens_entrada": 6500,
        "tokens_salida": 70,
        "modelo": "simulado"
    }
]

def llamar_modelo(historial: list[dict], sistema: str) -> dict:
    """Retorna secuencialmente una de las tres respuestas predefinidas."""
    global _contador
    resp = GUION[_contador % len(GUION)].copy()
    _contador += 1
    return resp