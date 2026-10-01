"""Lógica central del asistente y generación de bitácoras jsonl."""
from datetime import datetime
import json
import os
from pathlib import Path
import time
from dotenv import load_dotenv

from app import citas as mod_citas
from app import memoria as mod_memoria
from app import modelo as mod_modelo
from app import modelo_simulado as mod_simulado
from app import reglamento as mod_reglamento

load_dotenv()

class Asistente:
    def __init__(self, simulado: bool = False, canal: str = "cli", usuario: str = "local"):
        self.simulado = simulado
        self.canal = canal
        self.usuario = usuario
        self.historial = []
        self.max_mensajes = int(os.environ.get("MAX_MENSAJES", "6"))
        
        raiz = Path(__file__).resolve().parent.parent
        ruta_json = raiz / "data" / "reglamento_estudiantes_tecnm.json"
        ruta_prompt = raiz / "prompts" / "sistema.md"
        
        self.reglamento_data = mod_reglamento.cargar_reglamento(ruta_json)
        self.indice = mod_reglamento.indice_citas(self.reglamento_data)
        texto_reg = mod_reglamento.texto_para_prompt(self.reglamento_data)
        
        plantilla = ruta_prompt.read_text(encoding="utf-8")
        self.sistema = plantilla.replace("{REGLAMENTO}", texto_reg)
        self.corrida_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.contador_tg = 1

    def reset(self):
        self.historial = []

    def responder(self, pregunta: str, pregunta_id: str = None) -> str:
        t0 = time.time()
        mod_memoria.agregar(self.historial, "usuario", pregunta)
        enviados = mod_memoria.recortar(self.historial, self.max_mensajes)
        
        try:
            if self.simulado:
                res_modelo = mod_simulado.llamar_modelo(enviados, self.sistema)
            else:
                res_modelo = mod_modelo.llamar_modelo(enviados, self.sistema)
        except Exception as e:
            self.historial.pop()
            raise e

        segundos = round(time.time() - t0, 2)
        texto_resp = res_modelo["texto"]
        mod_memoria.agregar(self.historial, "modelo", texto_resp)

        citas_extraidas = mod_citas.extraer_citas(texto_resp)
        val = mod_citas.validar_citas(citas_extraidas, self.indice)
        invalidas = val["invalidas"]
        no_consta = "no consta" in texto_resp.lower()

        if invalidas:
            aviso = f"\n[Aviso] Estas citas no existen en el Reglamento: {', '.join(invalidas)}"
            respuesta_final = texto_resp + aviso
        else:
            respuesta_final = texto_resp

        if pregunta_id is None:
            if self.canal == "telegram":
                pid = f"TG-{self.contador_tg}"
                self.contador_tg += 1
            else:
                pid = "CLI"
        else:
            pid = pregunta_id

        self._guardar_bitacora(
            pid=pid,
            pregunta=pregunta,
            respuesta=texto_resp,
            citas=citas_extraidas,
            invalidas=invalidas,
            no_consta=no_consta,
            mensajes_enviados=len(enviados),
            tokens_in=res_modelo["tokens_entrada"],
            tokens_out=res_modelo["tokens_salida"],
            modelo_nombre=res_modelo["modelo"],
            segundos=segundos
        )

        return respuesta_final

    def _guardar_bitacora(self, pid, pregunta, respuesta, citas, invalidas, no_consta,
                          mensajes_enviados, tokens_in, tokens_out, modelo_nombre, segundos):
        raiz = Path(__file__).resolve().parent.parent
        carpeta_logs = raiz / "logs"
        carpeta_logs.mkdir(exist_ok=True)
        archivo_log = carpeta_logs / f"corrida-{self.corrida_id}.jsonl"

        registro = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "corrida": self.corrida_id,
            "modo": "simulado" if self.simulado else "real",
            "id": pid,
            "pregunta": pregunta,
            "respuesta": respuesta,
            "citas": citas,
            "citas_invalidas": invalidas,
            "no_consta": no_consta,
            "mensajes_enviados": mensajes_enviados,
            "tokens_entrada": tokens_in,
            "tokens_salida": tokens_out,
            "modelo": modelo_nombre,
            "segundos": segundos
        }

        if self.canal == "telegram":
            registro["canal"] = "telegram"
            registro["usuario"] = self.usuario

        with open(archivo_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")