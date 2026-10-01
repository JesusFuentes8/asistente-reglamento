"""Chat interactivo en la terminal."""
import sys
from app.asistente import Asistente

def main():
    simulado = "--simulado" in sys.argv
    print("=== Asistente del Reglamento de Estudiantes del TecNM ===")
    print("Aviso: Este asistente es únicamente informativo y no sustituye a las autoridades del plantel.")
    if simulado:
        print("[Modo simulado activado]")
    print("Comandos disponibles: /fuente, /reset, /salir\n")

    asistente = Asistente(simulado=simulado, canal="cli")

    while True:
        try:
            pregunta = input("Tú> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSesión finalizada.")
            break

        if not pregunta:
            continue

        if pregunta == "/salir":
            print("Hasta luego.")
            break
        elif pregunta == "/reset":
            asistente.reset()
            print("Memoria de la conversación reiniciada.")
            continue
        elif pregunta == "/fuente":
            doc = asistente.reglamento_data.get("documento", "Reglamento")
            aprobacion = asistente.reglamento_data.get("aprobacion", "Fecha no disponible")
            print(f"Fuente: {doc}\nAprobación: {aprobacion}")
            continue

        try:
            respuesta = asistente.responder(pregunta)
            print(f"\nAsistente:\n{respuesta}\n")
        except Exception as e:
            print(f"\n[Error al procesar la solicitud: {e}]\n")

if __name__ == "__main__":
    main()