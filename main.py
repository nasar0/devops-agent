import sys
import json
import os
import requests  
import uuid 
import time
from config.settings import config
from src.agent import ask_agent
from src.chatops import send_telegram_message, request_human_approval
from src.tools import AVAILABLE_TOOLS

# LISTA DE MEMORIA GLOBAL
HISTORIAL_CONTEXTO = []

def procesar_peticion(user_input: str):
    global HISTORIAL_CONTEXTO
    print(f"\n[INFO] [AGENTE] Procesando: '{user_input}'")
    
    # GENERAMOS UN TOKEN ÚNICO PARA ESTA OPERACIÓN
    # Esto evita que residuos de comandos pasados autoricen esta petición por error.
    TASK_TOKEN = str(uuid.uuid4())[:8]  # Tomamos un hash corto de 8 caracteres (Ej: 'a1b2c3d4')
    
    intento_actual = 1
    max_intentos = 5 
    ultimo_error = None
    comando_fallido = None 
    autorizado_por_humano = False 

    bloque_memoria = ""
    if HISTORIAL_CONTEXTO:
        bloque_memoria = "[CONTEXTO] CONTEXTO DE LA CONVERSACIÓN RECIENTE:\n"
        for msg in HISTORIAL_CONTEXTO:
            bloque_memoria += f"- {msg['rol']}: {msg['texto']}\n"
        bloque_memoria += "\n"

    prompt_actual = (
        f"{bloque_memoria}"
        f"[OBJETIVO] Petición actual del usuario: '{user_input}'"
    )

    while intento_actual <= max_intentos:
        if intento_actual > 1:
            prompt_actual = (
                f"{bloque_memoria}"
                f"[SISTEMA CRÍTICO DE AUTORREPARACIÓN - INTENTO {intento_actual}]\n"
                f"El comando que propusiste anteriormente falló en la terminal.\n\n"
                f"[OBJETIVO] Petición original del usuario: '{user_input}'\n"
                f"[ERROR] Comando erróneo que generaste: '{comando_fallido}'\n"
                f"[FALLO] Error de salida de la terminal:\n{ultimo_error}\n\n"
                f"[REGLAS] REGLAS CRÍTICAS DE REPARACIÓN:\n"
                f"1. Si el error dice 'No such file or directory', significa que la ruta que estás asumiendo NO existe. "
                f"¡PROHIBIDO volver a intentar el mismo comando o la misma ruta!\n"
                f"2. Estrategia de exploración: Si no encuentras el archivo, ejecuta un comando compuesto para listar el directorio "
                f"actual y ver dónde estás metido realmente (Ejemplo en Linux: 'pwd && ls -la' o 'find . -name \"*archivo*\"').\n"
                f"3. RECUERDA: Estás corriendo DENTRO de un contenedor Docker aislado. La raíz del proyecto es el directorio actual '.'. "
                f"Es muy probable que el archivo que buscas esté en la raíz o en una subcarpeta directa, no dentro de una carpeta repetida.\n"
                f"4. Corrige tu enfoque, descubre la ruta real y genera el JSON con el comando corregido."
            )

        print(f"  └── [PROCESANDO] [Intento {intento_actual}/{max_intentos}] Pensando...", end="\r", flush=True)
        
        ai_decision = ask_agent(prompt_actual)
        tool_name = ai_decision.get("tool_name")
        argument = ai_decision.get("argument")
        
        if not tool_name or tool_name not in AVAILABLE_TOOLS:
            print(f"\n[ERROR] La IA no pudo asociar tu petición con ninguna herramienta disponible.")
            return
            
        es_peligroso = False
        comando_a_ejecutar = argument

        if tool_name == "restart_container":
            es_peligroso = True
            comando_a_ejecutar = f"docker restart {argument}"
        elif tool_name == "herramienta_CLI":
            try:
                datos_cli = json.loads(argument) if isinstance(argument, str) and argument.strip().startswith("{") else argument
                if isinstance(datos_cli, dict):
                    comando_a_ejecutar = datos_cli.get("comando")
                    es_peligroso = datos_cli.get("peligro", False)
                else:
                    comando_a_ejecutar = argument
                    es_peligroso = True
            except Exception:
                comando_a_ejecutar = argument
                es_peligroso = True

        comando_fallido = comando_a_ejecutar
        print(f"  └── [EJECUCIÓN] [{tool_name}] -> [CLI] `{comando_a_ejecutar}` [Token: {TASK_TOKEN}]" + " " * 10)

        # CONTROL DE SEGURIDAD CRÍTICO MEDIANTE TOKENS ÚNICOS
        if es_peligroso:
            if autorizado_por_humano:
                print("  └── [OK] [AUTO-AUTORIZADO] Autorregulación protegida por el permiso previo del SRE.")
            else:
                # Le pasamos el TASK_TOKEN a la función de Telegram
                aprobado = request_human_approval(comando_a_ejecutar, TASK_TOKEN)
                if not aprobado:
                    print("  └── [BLOQUEADO] El administrador denegó la acción o expiró el Token. Abortando.")
                    send_telegram_message(f"[BLOQUEADO] Acción denegada [Token {TASK_TOKEN}]: `{comando_a_ejecutar}`")
                    return
                autorizado_por_humano = True
                send_telegram_message(f"[OK] Autorizado con éxito [Token {TASK_TOKEN}]: `{comando_a_ejecutar}`")

        try:
            if tool_name == "herramienta_CLI":
                result = AVAILABLE_TOOLS[tool_name](comando_a_ejecutar)
            elif argument and tool_name == "restart_container":
                result = AVAILABLE_TOOLS[tool_name](argument)
            else:
                result = AVAILABLE_TOOLS[tool_name]()
                
            if isinstance(result, str) and (result.startswith("❌ Error al ejecutar comando") or "No such file" in result or "cannot access" in result):
                print(f"  └── [WARN] Fallo detectado. Reajustando estrategia recursiva...")
                ultimo_error = result  
                intento_actual += 1
                continue 
                
            print(f"\n[OK] [ÉXITO] Tarea completada con éxito:")
            print(f"---------------------------------------------------\n{result}\n---------------------------------------------------")
            send_telegram_message(f"[INFO] *Resultado de la tarea* (`{tool_name}`):\n\n```\n{result}\n```")
            
            HISTORIAL_CONTEXTO.append({"rol": "Usuario", "texto": user_input})
            HISTORIAL_CONTEXTO.append({"rol": "Agente", "texto": f"Ejecuté {tool_name} con éxito para el comando `{comando_a_ejecutar}`."})
            
            if len(HISTORIAL_CONTEXTO) > 10:
                HISTORIAL_CONTEXTO = HISTORIAL_CONTEXTO[-5:]
            return

        except Exception as e:
            print(f"  └── [WARN] Fallo físico en la ejecución: {e}")
            ultimo_error = str(e)
            intento_actual += 1

    print(f"\n[CRÍTICO] [FAIL] El agente no pudo solucionar el problema tras {max_intentos} intentos.")
    send_telegram_message(f"[CRÍTICO] *Agente DevOps Falló*: No se pudo completar la tarea tras {max_intentos} intentos de autorreparación.")


def obtener_telegram_config():
    """Retorna el token y chat_id buscando variaciones en variables de entorno."""
    token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or getattr(config, 'telegram_token', None)
    chat_id = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or getattr(config, 'chat_id', None)
    return token, chat_id


def resetear_telegram():
    """Consume y purga todos los mensajes viejos pendientes en Telegram para iniciar limpios."""
    try:
        token, _ = obtener_telegram_config()
        if not token:
            return
            
        url_get = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){token}/getUpdates"
        res = requests.get(url_get, timeout=5).json()
        
        if res.get("ok") and res.get("result"):
            ultimo_update_id = res["result"][-1]["update_id"]
            requests.get(f"{url_get}?offset={ultimo_update_id + 1}", timeout=5)
            print("[INFO] [TELEGRAM] Cola de mensajes e historial antiguo purgado con éxito.")
    except Exception as e:
        print(f"[WARN] No se pudo purgar la cola de Telegram (Modo offline o error de red): {e}")


def iniciar_servicio_chatops():
    """Bucle infinito que escucha las peticiones entrantes directamente desde Telegram."""
    token, _ = obtener_telegram_config()
    if not token:
        print("[CRÍTICO] No se encontró el TELEGRAM_TOKEN en la configuración o entorno.")
        return

    url_updates = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){token}/getUpdates"
    offset = None
    
    print("[INFO] SERVICIO CHATOPS EN SEGUNDO PLANO ACTIVO")
    print("[INFO] Escuchando mensajes directamente desde tu chat de Telegram...")
    
    while True:
        try:
            params = {"timeout": 10, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
                
            response = requests.get(url_updates, params=params, timeout=15).json()
            
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        user_text = update["message"]["text"].strip()
                        
                        _, chat_id_autorizado = obtener_telegram_config()
                        if str(chat_id) != str(chat_id_autorizado):
                            print(f"[WARN] Intento de acceso no autorizado desde el Chat ID: {chat_id}")
                            continue
                            
                        if user_text.startswith("/"):
                            continue
                            
                        procesar_peticion(user_text)
                        
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n[INFO] Apagando el servicio de forma segura...")
            break
        except Exception as e:
            print(f"[ERROR] Error en el bucle del servicio de Telegram: {e}")
            time.sleep(5)


def main():
    print("========== AGENTE DEVOPS SRE INICIALIZADO ==========")
    print(f"[ENTORNO] Modo actual: {'NUBE (Groq)' if config.is_cloud else 'LOCAL (Ollama)'}")
    
    resetear_telegram()
    print("=======================================================\n")
    
    iniciar_servicio_chatops()

if __name__ == "__main__":
    main()