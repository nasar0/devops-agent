import sys
import json
import os
import requests  
from config.settings import config
from src.agent import ask_agent
from src.chatops import send_telegram_message, request_human_approval
from src.tools import AVAILABLE_TOOLS

#  LISTA DE MEMORIA GLOBAL (Mantiene el hilo de la conversación)
HISTORIAL_CONTEXTO = []

def procesar_peticion(user_input: str):
    global HISTORIAL_CONTEXTO
    print(f"\n🚀 [AGENTE] Procesando: '{user_input}'")
    
    intento_actual = 1
    max_intentos = 5 
    ultimo_error = None
    comando_fallido = None 
    autorizado_por_humano = False 

    # Construimos el bloque de memoria formateado para la IA
    bloque_memoria = ""
    if HISTORIAL_CONTEXTO:
        bloque_memoria = "👉 CONTEXTO DE LA CONVERSACIÓN RECIENTE:\n"
        for msg in HISTORIAL_CONTEXTO:
            bloque_memoria += f"- {msg['rol']}: {msg['texto']}\n"
        bloque_memoria += "\n"

    # El prompt inicial ahora incluye la memoria del pasado cercano
    prompt_actual = (
        f"{bloque_memoria}"
        f"🎯 Petición actual del usuario: '{user_input}'"
    )

    while intento_actual <= max_intentos:
        if intento_actual > 1:
            prompt_actual = (
                f"{bloque_memoria}"
                f"[SISTEMA CRÍTICO DE AUTORREPARACIÓN - INTENTO {intento_actual}]\n"
                f"El comando que propusiste anteriormente falló en la terminal.\n\n"
                f"🎯 Petición original del usuario: '{user_input}'\n"
                f"❌ Comando erróneo que generaste: '{comando_fallido}'\n"
                f"💥 Error de salida de la terminal:\n{ultimo_error}\n\n"
                f"👉 REGLAS CRÍTICAS DE REPARACIÓN:\n"
                f"1. Si el error dice 'No such file or directory', significa que la ruta que estás asumiendo NO existe. "
                f"¡PROHIBIDO volver a intentar el mismo comando o la misma ruta!\n"
                f"2. Estrategia de exploración: Si no encuentras el archivo, ejecuta un comando compuesto para listar el directorio "
                f"actual y ver dónde estás metido realmente (Ejemplo en Linux: 'pwd && ls -la' o 'find . -name \"*archivo*\"').\n"
                f"3. RECUERDA: Estás corriendo DENTRO de un contenedor Docker aislado. La raíz del proyecto es el directorio actual '.'. "
                f"Es muy probable que el archivo que buscas esté en la raíz o en una subcarpeta directa, no dentro de una carpeta repetida.\n"
                f"4. Corrige tu enfoque, descubre la ruta real y genera el JSON con el comando corregido."
            )

        print(f"  └── 🔄 [Intento {intento_actual}/{max_intentos}] Pensando...", end="\r", flush=True)
        
        ai_decision = ask_agent(prompt_actual)
        tool_name = ai_decision.get("tool_name")
        argument = ai_decision.get("argument")
        
        if not tool_name or tool_name not in AVAILABLE_TOOLS:
            print(f"\n❌ [Error] La IA no pudo asociar tu petición con ninguna herramienta disponible.")
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
        print(f"  └── 🛠️  [{tool_name}] -> 💻 `{comando_a_ejecutar}`" + " " * 25)

        if es_peligroso:
            if autorizado_por_humano:
                print("  └── ⚡ [AUTO-AUTORIZADO] Corrección bajo el permiso previo del SRE.")
            else:
                aprobado = request_human_approval(comando_a_ejecutar)
                if not aprobado:
                    print("  └── 🔴 [BLOQUEADO] El administrador denegó la acción. Abortando.")
                    send_telegram_message(f"❌ Acción denegada: `{comando_a_ejecutar}`")
                    return
                autorizado_por_humano = True
                send_telegram_message(f"⚡ Autorizado: `{comando_a_ejecutar}`")

        try:
            if tool_name == "herramienta_CLI":
                result = AVAILABLE_TOOLS[tool_name](comando_a_ejecutar)
            elif argument and tool_name == "restart_container":
                result = AVAILABLE_TOOLS[tool_name](argument)
            else:
                result = AVAILABLE_TOOLS[tool_name]()
                
            if isinstance(result, str) and (result.startswith("❌ Error al ejecutar comando") or "No such file" in result or "cannot access" in result):
                print(f"  └── ⚠️  Fallo detectado. Reajustando estrategia recursiva...")
                ultimo_error = result  
                intento_actual += 1
                continue 
                
            print(f"\n✅ [ÉXITO] Tarea completada con éxito:")
            print(f"---------------------------------------------------\n{result}\n---------------------------------------------------")
            send_telegram_message(f"📊 *Resultado de la tarea* (`{tool_name}`):\n\n```\n{result}\n```")
            
            # GUARDAR EN MEMORIA TRAS EL ÉXITO: Guardamos lo que pediste y la acción realizada
            HISTORIAL_CONTEXTO.append({"rol": "Usuario", "texto": user_input})
            HISTORIAL_CONTEXTO.append({"rol": "Agente", "texto": f"Ejecuté {tool_name} con éxito para el comando `{comando_a_ejecutar}`."})
            
            # Limitamos la memoria a los últimos 10 elementos para no engordar el prompt eternamente
            if len(HISTORIAL_CONTEXTO) > 10:
                HISTORIAL_CONTEXTO = HISTORIAL_CONTEXTO[-5:]
            return

        except Exception as e:
            print(f"  └── ⚠️  Fallo físico en la ejecución: {e}")
            ultimo_error = str(e)
            intento_actual += 1

    print(f"\n🛑 [FAIL] El agente no pudo solucionar el problema tras {max_intentos} intentos.")
    send_telegram_message(f"🚨 *Agente DevOps Falló*: No se pudo completar la tarea tras {max_intentos} intentos de autorreparación.")


def resetear_telegram():
    """Consume y purga todos los mensajes viejos pendientes en Telegram para iniciar limpios."""
    try:
        token = getattr(config, 'TELEGRAM_BOT_TOKEN', None) or os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            return
            
        url_get = f"https://api.telegram.org/bot{token}/getUpdates"
        res = requests.get(url_get, timeout=5).json()
        
        if res.get("ok") and res.get("result"):
            ultimo_update_id = res["result"][-1]["update_id"]
            requests.get(f"{url_get}?offset={ultimo_update_id + 1}", timeout=5)
            print("🧹 [TELEGRAM] Cola de mensajes e historial antiguo purgado con éxito.")
    except Exception as e:
        print(f"⚠️  No se pudo purgar la cola de Telegram (Modo offline o error de red): {e}")


def main():
    print("========== AGENTE DEVOPS SRE INICIALIZADO ==========")
    print(f"🌍 Modo actual: {'NUBE (Groq)' if config.is_cloud else 'LOCAL (Ollama)'}")
    print("🎈 Escribe 'salir' o presiona Ctrl+C para cerrar el agente.")
    
    resetear_telegram()
    print("=======================================================\n")
    
    while True:
        try:
            user_input = input("\n DevOps-Console> ").strip()
            
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\n Cerrando el Agente DevOps. ¡Buen trabajo!")
                break
                
            if not user_input:
                continue
                
            procesar_peticion(user_input)
            print("\n-------------------------------------------------------")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo de forma segura...")
            break
        except Exception as e:
            print(f"\n❌ Error crítico en el bucle: {e}")
            print("🔄 Reiniciando consola del agente...")

if __name__ == "__main__":
    main()