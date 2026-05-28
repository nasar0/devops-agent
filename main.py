import sys
import json
from config.settings import config
from src.agent import ask_agent
from src.chatops import send_telegram_message, request_human_approval
from src.tools import AVAILABLE_TOOLS

def procesar_peticion(user_input: str):
    print(f"\n💬 Usuario pide: '{user_input}'")
    
    intento_actual = 1
    max_intentos = 3
    prompt_actual = user_input
    
    # Variables de rastreo de errores para el Saneamiento
    ultimo_error = None
    comando_fallido = None 

    while intento_actual <= max_intentos:
        if intento_actual > 1:
            print(f"\n🔄 [AUTORREPARACIÓN] Intento {intento_actual}/{max_intentos}...")
            # Construimos un contexto súper agresivo con el historial del error
            prompt_actual = (
                f"[SISTEMA CRÍTICO DE AUTORREPARACIÓN - INTENTO {intento_actual}]\n"
                f"El comando que propusiste anteriormente falló estrepitosamente en la terminal.\n\n"
                f"🎯 Petición original del usuario: '{user_input}'\n"
                f"❌ Comando erróneo que generaste: '{comando_fallido}'\n"
                f"💥 Error de salida de la terminal:\n{ultimo_error}\n\n"
                f"👉 INSTRUCCIÓN DE REPARACIÓN:\n"
                f"1. Analiza el error sintáctico o de permisos.\n"
                f"2. Si estás en Windows, evita poner espacios corruptos (NUNCA generes cosas como '.      est').\n"
                f"3. Si la petición requiere varios pasos secuenciales para completarse con éxito, "
                f"puedes encadenar comandos utilizando el punto y coma ';' (en Windows) o '&&' (en Linux).\n"
                f"4. Devuelve el JSON con el comando corregido y limpio."
            )

        print("🧠 Pensando...")
        ai_decision = ask_agent(prompt_actual)
        tool_name = ai_decision.get("tool_name")
        argument = ai_decision.get("argument")
        thought = ai_decision.get("thought")
        
        print(f"🤔 Pensamiento de la IA: {thought}")
        
        if not tool_name or tool_name not in AVAILABLE_TOOLS:
            print("❌ La IA no pudo asociar tu petición con ninguna herramienta disponible.")
            return
            
        print(f"🛠️  Herramienta seleccionada: {tool_name}")
        
        es_peligroso = False
        comando_a_ejecutar = argument

        # Desempaquetar comandos de forma segura
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

        # 💾 Guardamos el comando actual antes de ejecutarlo para el rastreador de fallos
        comando_fallido = comando_a_ejecutar

        if comando_a_ejecutar:
            print(f"💻 Comando asignado: {comando_a_ejecutar}")

        # Freno de mano interactivo
        if es_peligroso:
            aprobado = request_human_approval(comando_a_ejecutar)
            if not aprobado:
                print("🔴 [BLOQUEADO] El administrador denegó la acción. Abortando.")
                send_telegram_message(f"❌ Acción denegada: `{comando_a_ejecutar}`")
                return
            send_telegram_message(f"⚡ Autorizado: `{comando_a_ejecutar}`")

        # Ejecución real en caliente
        print("🚀 Ejecutando comando en el sistema...")
        try:
            if tool_name == "herramienta_CLI":
                result = AVAILABLE_TOOLS[tool_name](comando_a_ejecutar)
            elif argument and tool_name == "restart_container":
                result = AVAILABLE_TOOLS[tool_name](argument)
            else:
                result = AVAILABLE_TOOLS[tool_name]()
                
            # Evaluar si la herramienta del sistema reportó un error real de ejecución
            if isinstance(result, str) and result.startswith("❌ Error al ejecutar comando"):
                print(result) 
                ultimo_error = result  # Guardamos el reporte para el prompt del próximo intento
                intento_actual += 1
                continue # 🔁 Reintenta saltando al principio del bucle while sin romper el flujo
                
            # Si el comando fue exitoso, rompemos el bucle y enviamos reporte
            print(result)
            send_telegram_message(f"📊 *Resultado de la tarea* (`{tool_name}`):\n\n```\n{result}\n```")
            return

        except Exception as e:
            ultimo_error = str(e)
            print(f"❌ Falló la ejecución física: {e}")
            intento_actual += 1

    print(f"\n🛑 [FAIL] El agente no pudo solucionar el problema tras {max_intentos} intentos.")
    send_telegram_message(f"🚨 *Agente DevOps Falló*: No se pudo completar la tarea tras {max_intentos} intentos de autorreparación.")

def main():
    print("========== AGENTE DEVOPS SRE INICIALIZADO ==========")
    print(f"🌍 Modo actual: {'NUBE (Groq)' if config.is_cloud else 'LOCAL (Ollama)'}")
    print("🎈 Escribe 'salir' o presiona Ctrl+C para cerrar el agente.")
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