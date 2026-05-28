import sys
import json
from config.settings import config
from src.agent import ask_agent
from src.chatops import send_telegram_message, request_human_approval
from src.tools import AVAILABLE_TOOLS

# Procesa una petición con un bucle de autorreparación si el comando falla.

def procesar_peticion(user_input: str):
    print(f"\n💬 Usuario pide: '{user_input}'")
    
    intento_actual = 1
    max_intentos = 3
    prompt_actual = user_input
    ultimo_error = None

    while intento_actual <= max_intentos:
        if intento_actual > 1:
            print(f"\n🔄 [AUTORREPARACIÓN] Intento {intento_actual}/{max_intentos}...")
            # Le reformulamos la petición a la IA pasándole el error que cometió antes
            prompt_actual = (
                f"Tu comando anterior falló.\n"
                f"Petición original del usuario: '{user_input}'\n"
                f"Error obtenido en la terminal:\n{ultimo_error}\n"
                f"Por favor, analiza el error, corrige los espacios, rutas o sintaxis, y genera el comando corregido."
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

        # Desempaquetar comandos
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

        if comando_a_ejecutar:
            print(f"💻 Comando asignado: {comando_a_ejecutar}")

        # Freno de mano (Solo se activa en el primer intento para no dar la paliza en cada corrección, 
        # o puedes dejar que pida permiso siempre. Por seguridad, pedimos siempre en comandos peligrosos)
        if es_peligroso:
            aprobado = request_human_approval(comando_a_ejecutar)
            if not aprobado:
                print("🔴 [BLOQUEADO] El administrador denegó la acción. Abortando.")
                send_telegram_message(f"❌ Acción denegada: `{comando_a_ejecutar}`")
                return
            send_telegram_message(f"⚡ Autorizado: `{comando_a_ejecutar}`")

        # Ejecución real
        print("🚀 Ejecutando comando en el sistema...")
        try:
            if tool_name == "herramienta_CLI":
                result = AVAILABLE_TOOLS[tool_name](comando_a_ejecutar)
            elif argument and tool_name == "restart_container":
                result = AVAILABLE_TOOLS[tool_name](argument)
            else:
                result = AVAILABLE_TOOLS[tool_name]()
                
            # Evaluamos si el resultado de nuestra herramienta CLI fue un error de terminal
            if isinstance(result, str) and result.startswith("❌ Error al ejecutar comando"):
                print(result) # Imprimimos el error en la consola del PC
                ultimo_error = result
                intento_actual += 1
                continue # Reintenta el bucle saltando a la autorreparación
                
            # Si el comando fue exitoso, salimos del bucle
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
    print( "🎈 Escribe 'salir' o presiona Ctrl+C para cerrar el agente.")
    print("=======================================================\n")
    
    # BUCLE INTERACTIVO: No se rompe, se queda escuchando
    while True:
        try:
            # Pedimos el input directamente en caliente por consola
            user_input = input("\n DevOps-Console> ").strip()
            
            # Condición de salida limpia
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\n Cerrando el Agente DevOps. ¡Buen trabajo!")
                break
                
            # Si el usuario le da a Enter sin escribir nada, volvemos a preguntar
            if not user_input:
                continue
                
            # Procesamos la orden sin salirnos del bucle principal
            procesar_peticion(user_input)
            
            print("\n-------------------------------------------------------")
            
        except KeyboardInterrupt:
            # Captura limpia si pulsas Ctrl+C en la consola
            print("\n\n👋 Saliendo de forma segura...")
            break
        except Exception as e:
            print(f"\n❌ Error crítico en el bucle: {e}")
            print("🔄 Reiniciando consola del agente...")

if __name__ == "__main__":
    main()