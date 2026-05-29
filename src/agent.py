import json
import requests
import platform 
from config.settings import config

"""
    Orquesta la petición del usuario inyectando dinámicamente el Sistema Operativo actual
    con un System Prompt blindado y ultra-potente orientado a CLI puro.
"""
def ask_agent(user_prompt: str) -> dict:

    sistema_operativo = platform.system()
    
    # Guías de sintaxis nativas agresivas y concisas
    if sistema_operativo == "Windows":
        guia_sintaxis = (
            "1. Estás en Windows PowerShell (NO cmd, NO bash).\n"
            "2. Para ejecutar comandos múltiples en una sola línea, usa ÚNICAMENTE el punto y coma ';' (Ejemplo: comando1; comando2). PROHIBIDO usar '&&'.\n"
            "3. Evita corrupciones de texto. NUNCA agregues espacios en blanco corruptos ni tabulaciones dentro de rutas o nombres (Ejemplo: usa 'test', PROHIBIDO generar '.      est' o '.   est').\n"
            "4. Para crear directorios y archivos con texto usa la sintaxis limpia: New-Item -ItemType Directory -Name 'test'; Set-Content -Path 'test/test.txt' -Value 'contenido'\n"
            "5. Para ver espacio en disco usa 'Get-PSDrive' o 'Get-Volume'. Para memoria usa 'Get-CimInstance Win32_OperatingSystem'."
        )
    else:
        guia_sintaxis = (
            "1. Estás en Linux/Unix Bash.\n"
            "2. Para ejecutar comandos múltiples usa '&&' si el segundo depende del primero, o ';' para ejecución secuencial.\n"
            "3. Asegúrate de que las rutas relativas sean válidas según el estándar de directorios de Linux.\n"
            "4. Para ver espacio en disco usa obligatoriamente 'df -h'. Para memoria o CPU usa 'free -m' o 'top -b -n 1 | head -n 20'. Para listar contenedores usa 'docker ps -a'."
        )

    # SYSTEM PROMPT BLINDADO ORIENTADO A CLI PURO (SIN FUNCIONES VIEJAS)
    system_instructions = (
        f"[PERFIL Y ROL]\n"
        f"Eres un agente SRE/DevOps experto, riguroso y automatizado que gestiona sistemas Linux y Windows.\n\n"
        
        f"[ENTORNO DE EJECUCIÓN CRÍTICO]\n"
        f"- Sistema Operativo anfitrión: {sistema_operativo}\n"
        f"- Restricción absoluta: Cualquier comando que generes debe ejecutarse nativamente en {sistema_operativo}.\n\n"
        
        f"[REGLAS DE SINTAXIS NATIVA]\n"
        f"{guia_sintaxis}\n\n"
        
        f"[HERRAMIENTAS DISPONIBLES]\n"
        f"- 'herramienta_CLI': Es la ÚNICA herramienta activa en el sistema. Debes usarla para CUALQUIER petición del usuario (diagnósticos, discos, contenedores, manipulación de archivos, etc.).\n"
        f"En el campo 'argument' debes meter un string que sea obligatoriamente un objeto JSON plano con el comando nativo real y su nivel de riesgo bajo este formato exacto:\n"
        f"   {{\"comando\": \"tu_comando_nativo_aqui\", \"peligro\": true/false}}\n\n"
        
        f"[POLÍTICA DE EVALUACIÓN DE RIESGO ('peligro')]\n"
        f"- 'peligro': true -> Obligatorio para CUALQUIER comando de escritura o alteración que cree, borre, edite, reinicie, instale o modifique archivos, contenedores o servicios (Ejemplos: mkdir, rm, echo ..., touch, New-Item, Set-Content, del, rmdir, docker restart, docker rm, apt, pip, wget, curl).\n"
        f"- 'peligro': false -> Exclusivo para comandos pasivos de pura lectura, visualización, diagnóstico o red (Ejemplos: df -h, free -m, docker ps -a, ping, ls, dir, netstat, uptime, hostname).\n\n"
        
        f"[REGLA CRÍTICA DE RESPUESTA - FORMATO JSON ESTRICTO]\n"
        f"Debes responder ÚNICAMENTE con un objeto JSON válido. Sin textos explicativos antes o después, sin bloques de código Markdown (```json). Tu respuesta debe ser parseable directamente por json.loads().\n"
        f"Estructura exacta del JSON de salida:\n"
        f"{{\n"
        f"  \"tool_name\": \"herramienta_CLI\",\n"
        f"  \"argument\": \"{{\\\"comando\\\": \\\"tu_comando_aqui\\\", \\\"peligro\\\": false}}\",\n"
        f"  \"thought\": \"Explicación técnica de qué comando nativo se va a lanzar\"\n"
        f"}}"
    )

    # --- Bloque de conexiones e infraestructura de APIs ---
    if config.is_cloud:
        url = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"
        headers = {
            "Authorization": f"Bearer {config.groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }
        
        try:
            response_obj = requests.post(url, json=payload, headers=headers, timeout=15)
            res = response_obj.json()
            content = res["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"❌ Error al conectar con Groq Cloud: {e}")
            if 'response_obj' in locals():
                print(f"📄 Respuesta cruda de la API: {response_obj.text}")
            return {"tool_name": "herramienta_CLI", "argument": '{"comando": "echo Error api", "peligro": false}', "thought": "Fallo en la API de la nube."}
            
    else:
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0}
        }
        
        try:
            res = requests.post(url, json=payload, timeout=20).json()
            content = res["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"❌ Error al conectar con Ollama Local: {e}")
            return {"tool_name": "herramienta_CLI", "argument": '{"comando": "echo Error ollama", "peligro": false}', "thought": "Ollama local no disponible."}