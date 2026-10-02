# Asistente del Reglamento de Estudiantes del TecNM

- **Alumno:** FUENTES HERNANDEZ JESUS DANIEL
- **Número de control:** 22071262
- **Asignatura:** Desarrollo de Agentes Inteligentes (ACD-2504), grupo 850P-A
- **Docente:** D. C. C. Alejandro Estrada Padilla
- **Trabajo:** Práctica 3 · Unidad 1
- **Entrega:** 30 de septiembre de 2026

## Qué hace

Es un agente conversacional inteligente diseñado para orientar a la comunidad estudiantil respecto al Reglamento de Estudiantes del TecNM. A diferencia de pegar un archivo PDF en un chat comercial, este asistente restringe estrictamente su contexto al articulado oficial inyectado dinámicamente en el prompt del sistema, implementa un filtro post-generación de extracción y validación sintáctica de citas normativas contra un índice canónico de 126 claves, y rechaza consultas administrativas o ajenas declarando explícitamente "no consta en el Reglamento de Estudiantes".

## Arquitectura

[ Usuario (CLI / Telegram) ]
|
v
[ app/bot.py / app/cli.py ]
|
v
[ app/memoria.py ] ---> (Mantiene ventana corta de max_mensajes)
|
v
[ app/asistente.py ] <--- [ prompts/sistema.md + data/reglamento...json ]
|
v
[ app/modelo.py ] -----> [ Google Gemini API (gemini-3.8-flash) ]
|
v
[ app/citas.py ] ------> (Extracción regex y validación contra índice)
|
v
[ logs/corrida-*.jsonl ] (Registro estructurado de auditoría)

## Requisitos e instalación

Para ejecutar el entorno local en Windows PowerShell:

```powershell
git clone <url-del-repositorio>
cd asistente-reglamento
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

## Variables de entorno

Copiar .env.example a .env configurando los siguientes valores (este archivo .env está estrictamente ignorado por .gitignore y jamás debe subirse al repositorio):

GEMINI_API_KEY: Clave de autenticación de Google AI Studio.

GEMINI_MODEL: Modelo utilizado (gemini-3.8-flash).

MAX_MENSAJES: Cantidad máxima de mensajes en el historial de contexto (6).

TELEGRAM_BOT_TOKEN: Token proporcionado por @BotFather.

TELEGRAM_USUARIOS_PERMITIDOS: Lista de IDs numéricos de Telegram autorizados (separados por comas).

## Cómo usarlo

Chat interactivo en terminal:

Modo simulado: python -m app.cli --simulado

Modo real: python -m app.cli

Evaluación por lotes:

Modo simulado: python -m app.lote data/preguntas_prueba.json --simulado

Modo real: python -m app.lote data/preguntas_prueba.json

Pregunta específica: python -m app.lote data/preguntas_prueba.json --solo R01

Pruebas unitarias:

Ejecutar suite: python -m pruebas.prueba_citas

## Bot de Telegram


Crear el bot enviando /newbot al usuario @BotFather en Telegram.

Copiar el token generado y asignarlo a TELEGRAM_BOT_TOKEN dentro de .env.

Para obtener su ID numérico, inicie el bot y envíele un mensaje; el bot responderá indicando su ID personal no autorizado.

Coloque dicho identificador numérico en TELEGRAM_USUARIOS_PERMITIDOS dentro de .env.

Comandos para iniciar el bot:

Simulado: python -m app.bot --simulado

Real: python -m app.bot

El bot admite los comandos /start, /fuente y /reset.

Captura de evidencia disponible en evidencia/telegram.png.


## Estructura del proyecto

app/asistente.py: Coordinador central del flujo de consulta, validación y bitácora.

app/bot.py: Implementación asíncrona del bot de Telegram con control de acceso.

app/citas.py: Extracción por expresiones regulares y validación de citas normativas.

app/cli.py: Interfaz de chat interactivo por consola.

app/lote.py: Ejecutor automatizado del banco de pruebas de 18 llamadas.

app/memoria.py: Gestión de recorte de contexto e historial de mensajes.

app/modelo.py: Conector oficial con el SDK google-genai para la API de Gemini.

app/modelo_simulado.py: Stub local con guion cíclico para pruebas sin consumo de red.

app/reglamento.py: Parser y formateador del JSON oficial y generador de índice canónico.

data/: Documentos normativos y preguntas de prueba.

evaluacion/: Archivos de respuestas esperadas y evaluación de resultados.

evidencia/: Captura de pantalla de la interacción con el bot.

logs/: Archivos .jsonl con la trazabilidad y métricas de cada llamada.

prompts/: Plantilla del sistema con directivas de rol y formato.

pruebas/: Suite de pruebas unitarias locales.

## Decisiones de diseño

El prompt del sistema impone un formato estricto de tres renglones (Respuesta:, Fundamento:, Confianza:) para desacoplar el razonamiento jurídico de la fundamentación textual. Las citas se normalizan al formato Art. N, fracc. R separadas por punto y coma. Se fijó MAX_MENSAJES=6 para permitir un contexto conversacional de 3 turnos (pregunta/respuesta) sin desbordar la ventana ni diluir la instrucción del sistema. Cuando una cita es inválida, el validador añade un aviso explícito [Aviso] Estas citas no existen en el Reglamento: sin alterar la respuesta generada; si la llamada a la API falla, se descarta el turno del usuario del historial para evitar desincronización de roles y se relanza la excepción.
## Resultados

Respuestas correctas: 18 de 18 casos evaluados.

Citas inválidas generadas en la corrida final: 0.

Tokens consumidos promedio: ~6,530 de entrada y ~720 de salida por turno.

Para un documento más extenso como el Manual de Lineamientos (estimado en 50,000 tokens), el costo computacional por turno aumentaría considerablemente, por lo que sería conveniente evolucionar hacia una arquitectura RAG (Retrieval-Augmented Generation) con búsqueda semántica previa en lugar de inyección completa de contexto.

## Límites y ética

El asistente es estrictamente un orientador informativo y no constituye una autoridad oficial del TecNM ni sustituye las facultades de la Dirección o Servicios Escolares. El sistema anonimiza los identificadores de Telegram mediante un hash SHA-256 de 10 caracteres, no almacena datos personales sensibles y orienta de forma neutral en casos de acoso o faltas graves remitiendo por escrito ante el Comité Académico.

## Declaración de uso de IA

Se utilizó Gemini como copiloto de desarrollo para la refactorización de scripts en Windows PowerShell, depuración de llamadas al SDK google-genai y redacción de tablas comparativas. Se corrigió manualmente la persistencia del archivo .gitignore, la normalización de claves unificadas y la estructura de consolidación de bitácoras.