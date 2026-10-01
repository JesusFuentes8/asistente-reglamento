"""Extracción y validación de citas normativas."""
import re

def extraer_citas(texto: str) -> list[str]:
    """Extrae citas normativas preservando el orden y sin duplicar."""
    # Coincide primero con fracción o numeral; si no tiene ninguna, toma el artículo solo.
    patron = re.compile(
        r'(?:art\.?|art[ií]culo)\s+(\d+)(?:\s*,?\s*(?:fracc\.?|fracci[oó]n)\s+([ivxlcdm]+)|\s*,?\s*numeral\s+(\d+))?',
        re.IGNORECASE
    )
    
    citas: list[str] = []
    vistos: set[str] = set()

    for match in patron.finditer(texto):
        num_art = match.group(1)
        fracc = match.group(2)
        numeral = match.group(3)

        if fracc:
            clave = f"{num_art}.{fracc.upper()}"
        elif numeral:
            clave = f"{num_art}.{numeral}"
        else:
            clave = str(num_art)

        if clave not in vistos:
            vistos.add(clave)
            citas.append(clave)

    return citas

def validar_citas(citas: list[str], indice: set[str]) -> dict[str, list[str]]:
    """Separa las citas en válidas e inválidas según el índice oficial."""
    validas = []
    invalidas = []
    
    for c in citas:
        if c in indice:
            validas.append(c)
        else:
            invalidas.append(c)
            
    return {"validas": validas, "invalidas": invalidas}