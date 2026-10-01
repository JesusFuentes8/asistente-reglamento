"""Ejecutor del banco de pruebas por lotes."""
import json
from pathlib import Path
import sys
import time
from app.asistente import Asistente

def main():
    if len(sys.argv) < 2:
        print("Uso: python -m app.lote <ruta_json> [--simulado] [--solo ID1,ID2...]")
        sys.exit(1)

    ruta_json = Path(sys.argv[1])
    simulado = "--simulado" in sys.argv

    solo_ids = set()
    if "--solo" in sys.argv:
        idx = sys.argv.index("--solo")
        if idx + 1 < len(sys.argv):
            raw = sys.argv[idx + 1]
            solo_ids = {i.strip() for i in raw.split(",") if i.strip()}

    with open(ruta_json, "r", encoding="utf-8") as f:
        datos_prueba = json.load(f)

    asistente = Asistente(simulado=simulado, canal="lote")
    print(f"Iniciando evaluación {'(simulada)' if simulado else '(real)'}...")

    # Preguntas sueltas
    for item in datos_prueba.get("preguntas", []):
        pid = item["id"]
        if solo_ids and pid not in solo_ids:
            continue

        asistente.reset()
        pregunta = item["pregunta"]
        print(f"[{pid}] Pregunta: {pregunta}")
        try:
            resp = asistente.responder(pregunta, pregunta_id=pid)
            print(f"[{pid}] OK -> Citas extraídas / respuesta registrada.")
        except Exception as e:
            print(f"[{pid}] ERROR al consultar el modelo: {e}")

        if not simulado:
            time.sleep(4)

    # Conversaciones con memoria compartida
    for conv in datos_prueba.get("conversaciones", []):
        cid = conv["id"]
        asistente.reset()
        
        turnos = conv.get("turnos", [])
        for i, turno_preg in enumerate(turnos, start=1):
            tid = f"{cid}-{i}"
            if solo_ids and cid not in solo_ids and tid not in solo_ids:
                continue

            print(f"[{tid}] Pregunta: {turno_preg}")
            try:
                resp = asistente.responder(turno_preg, pregunta_id=tid)
                print(f"[{tid}] OK -> Turno procesado.")
            except Exception as e:
                print(f"[{tid}] ERROR en conversación: {e}")
                break

            if not simulado:
                time.sleep(4)

if __name__ == "__main__":
    main()