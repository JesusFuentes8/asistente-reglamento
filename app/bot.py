"""Bot de Telegram para atención a estudiantes del TecNM."""
import asyncio
import hashlib
import logging
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from app.asistente import Asistente

load_dotenv()

logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def leer_permitidos(texto: str) -> set[int]:
    """Parsea una lista de identificadores numéricos separados por comas."""
    if not texto:
        return set()
    permitidos = set()
    for item in texto.split(","):
        limpio = item.strip()
        if limpio.isdigit():
            permitidos.add(int(limpio))
    return permitidos

def partir_mensaje(texto: str, limite: int = 4096) -> list[str]:
    """Divide mensajes largos procurando no cortar palabras o renglones."""
    if len(texto) <= limite:
        return [texto]
    partes = []
    while len(texto) > limite:
        corte = texto.rfind("\n", 0, limite)
        if corte == -1:
            corte = texto.rfind(" ", 0, limite)
        if corte == -1:
            corte = limite
        partes.append(texto[:corte].strip())
        texto = texto[corte:].strip()
    if texto:
        partes.append(texto)
    return partes

def usuario_anonimo(user_id: int) -> str:
    """Genera un hash SHA-256 de 10 caracteres a partir del id numérico."""
    return hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:10]

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    permitidos = context.bot_data["permitidos"]
    
    if permitidos and user_id not in permitidos:
        await update.effective_message.reply_text(
            f"Acceso restringido. Este bot es privado.\nTu ID de usuario es: {user_id}"
        )
        return

    mensaje_bienvenida = (
        "¡Hola! Soy el Asistente del Reglamento de Estudiantes del TecNM.\n\n"
        "Puedo orientarte sobre derechos, obligaciones, faltas y sanciones institucionales.\n\n"
        "Aviso importante:\n"
        "• No soy una autoridad del plantel y mis respuestas son únicamente informativas.\n"
        "• Aviso de privacidad: No compartas datos personales sensibles. Las interacciones son registradas de forma anónima.\n\n"
        "Comandos disponibles: /fuente, /reset"
    )
    await update.effective_message.reply_text(mensaje_bienvenida)

async def cmd_fuente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    asistente = context.bot_data["asistentes"].get(chat_id)
    if not asistente:
        asistente = Asistente(
            simulado=context.bot_data["simulado"],
            canal="telegram",
            usuario=usuario_anonimo(update.effective_user.id)
        )
        context.bot_data["asistentes"][chat_id] = asistente

    doc = asistente.reglamento_data.get("documento", "Reglamento")
    aprobacion = asistente.reglamento_data.get("aprobacion", "Fecha no disponible")
    await update.effective_message.reply_text(f"Fuente oficial:\n{doc}\nAprobación: {aprobacion}")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in context.bot_data["asistentes"]:
        context.bot_data["asistentes"][chat_id].reset()
    await update.effective_message.reply_text("La memoria de esta conversación ha sido reiniciada.")

async def con_escribiendo(chat, funcion, *args):
    """Muestra el estado 'escribiendo...' mientras se ejecuta la función en otro hilo."""
    tarea = asyncio.ensure_future(asyncio.to_thread(funcion, *args))
    while not tarea.done():
        await chat.send_action(ChatAction.TYPING)
        await asyncio.wait([tarea], timeout=4)
    return tarea.result()

async def atender_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    permitidos = context.bot_data["permitidos"]
    
    if permitidos and user_id not in permitidos:
        await update.effective_message.reply_text(
            f"Acceso restringido. Este bot es privado.\nTu ID de usuario es: {user_id}"
        )
        return

    chat_id = update.effective_chat.id
    texto = update.effective_message.text

    if chat_id not in context.bot_data["asistentes"]:
        context.bot_data["asistentes"][chat_id] = Asistente(
            simulado=context.bot_data["simulado"],
            canal="telegram",
            usuario=usuario_anonimo(user_id)
        )

    asistente = context.bot_data["asistentes"][chat_id]

    try:
        respuesta = await con_escribiendo(update.effective_chat, asistente.responder, texto)
        for trozo in partir_mensaje(respuesta):
            await update.effective_message.reply_text(trozo)
    except Exception as e:
        await update.effective_message.reply_text(
            "Lo siento, ocurrió un error al consultar el reglamento. Por favor, intenta de nuevo más tarde."
        )

def main():
    simulado = "--simulado" in sys.argv
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    permitidos_str = os.environ.get("TELEGRAM_USUARIOS_PERMITIDOS", "")
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN no está definido en el archivo .env")
        sys.exit(1)

    permitidos = leer_permitidos(permitidos_str)

    app = ApplicationBuilder().token(token).build()
    app.bot_data["asistentes"] = {}
    app.bot_data["permitidos"] = permitidos
    app.bot_data["simulado"] = simulado

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("fuente", cmd_fuente))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, atender_mensaje))

    print(f"Bot de Telegram iniciado {'(simulado)' if simulado else '(real)'}. Presiona Ctrl+C para detener.")
    app.run_polling()

if __name__ == "__main__":
    main()