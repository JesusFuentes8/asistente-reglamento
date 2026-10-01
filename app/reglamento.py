"""Módulo para procesar y formatear el Reglamento de Estudiantes del TecNM."""
import json
from pathlib import Path

def cargar_reglamento(ruta: str | Path) -> dict:
    """Carga el archivo JSON del reglamento con codificación UTF-8."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def texto_para_prompt(reglamento: dict) -> str:
    """Genera el texto estructurado del reglamento para inyectar en el prompt."""
    lineas = [
        "REGLAMENTO DE ESTUDIANTES DEL TECNOLÓGICO NACIONAL DE MÉXICO"
    ]
    
    titulo_actual = None
    
    for art in reglamento.get("articulos", []):
        titulo = art.get("titulo")
        if titulo and titulo != titulo_actual:
            titulo_actual = titulo
            lineas.append(f"\n{titulo_actual.upper()}\n")
            
        num = art["numero"]
        lineas.append(f"Art. {num}. {art['encabezado']}")
        
        for fracc in art.get("fracciones", []):
            f_id = fracc["id"]
            texto = fracc["texto"]
            lineas.append(f"Art. {num}, fracc. {f_id}. {texto}")
            
        if "cierre" in art:
            lineas.append(f"Art. {num} (párrafo final). {art['cierre']}")

    transitorios = reglamento.get("transitorios", [])
    if transitorios:
        lineas.append("\nTRANSITORIOS\n")
        for t in transitorios:
            lineas.append(f"{t['id']}. {t['texto']}")
            
    return "\n".join(lineas)

def indice_citas(reglamento: dict) -> set[str]:
    """Genera el conjunto de 126 citas válidas ('9', '9.II', '14.3', etc.)."""
    indice = set()
    for art in reglamento.get("articulos", []):
        num = str(art["numero"])
        indice.add(num)
        for fracc in art.get("fracciones", []):
            f_id = str(fracc["id"])
            indice.add(f"{num}.{f_id}")
    return indice