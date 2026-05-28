# 🤖 DevOps & SRE Autonomous AI Agent

Un agente autónomo avanzado de ingeniería de confiabilidad de sitios (SRE) y operaciones de desarrollo (DevOps). Diseñado para ejecutarse de forma híbrida en entornos **Windows (PowerShell)** y **Linux (Bash)**, interactuando nativamente con el sistema operativo bajo un estricto control de seguridad y capacidades de autorreparación en tiempo real.

---

## 🚀 Características Principales

*   **🧠 Cerebro Híbrido Dinámico:** Capaz de conmutar entre la nube de alto rendimiento con **Groq Cloud (Llama 3.3)** y ejecución local 100% privada mediante **Ollama (Llama 3)**.
*   **💻 Abstracción Automática del Entorno:** Autodetecta el sistema operativo anfitrión. Adapta la sintaxis de los comandos en tiempo real evitando conflictos entre operadores (como la conversión automática de `&&` a `;` en entornos Windows PowerShell antiguos).
*   **🛑 Freno de Mano por Telegram (Human-in-the-Loop):** Clasifica de forma autónoma el nivel de riesgo de cada comando. Si detecta acciones de escritura o modificación (`mkdir`, `rm`, `docker restart`), congela el hilo de ejecución y solicita aprobación interactiva al administrador vía Telegram.
*   **🔄 Bucle de Autorreparación (Self-Healing):** Si un comando CLI falla en la terminal, el agente captura el código de salida y el mensaje de error nativo, reformula el contexto y realiza hasta **3 intentos de depuración autónoma** para corregir la sintaxis.
*   **📟 Consola Interactiva REPL:** Interfaz continua por consola que mantiene al agente en escucha activa sin interrupción del servicio ante fallos del sistema o excepciones de codificación de caracteres.

---

## 🛠️ Herramientas Integradas

El agente mapea el lenguaje natural del usuario y lo transforma en llamadas a funciones estructuradas o comandos globales:

| Herramienta | Tipo de Acción | Descripción |
| :--- | :--- | :--- |
| `check_disk_space` | Lectura / Diagnóstico | Monitoreo del espacio en discos del sistema. |
| `check_cpu_memory` | Lectura / Diagnóstico | Muestreo de consumos de RAM y CPU de forma nativa. |
| `list_docker_containers` | Lectura / Diagnóstico | Listado de contenedores e infraestructura Docker actual. |
| `restart_container` | Escritura (**Crítica**) | Reinicio controlado de microservicios y contenedores. |
| `herramienta_CLI` | Dinámica (**Evaluada**) | Intérprete genérico para cualquier comando del sistema operativo. |

---

## 📦 Requisitos e Instalación

### 1. Clonar el repositorio y acceder
```bash
cd "C:\Users\Administrador\Desktop\Arminet\pagina web\Nueva Carpeta\devops-agent"

```

### 2. Configurar el Entorno Virtual (Venv)

```powershell
# En Windows (PowerShell)
.\venv\Scripts\activate

```

### 3. Configuración de Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto con la siguiente estructura:

```env
IA_MODE=CLOUD or LOCAL
GROQ_KEY=YOUR_API_KEY_OF_GROQ
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID
```

---

## 🕹️ Modo de Uso

Para lanzar la consola interactiva infinita del agente SRE, ejecuta:

```powershell
python main.py

```

### Ejemplo de flujo interactivo en la terminal:

```text
========== 🤖 AGENTE DEVOPS SRE INICIALIZADO ==========
🌍 Modo actual: NUBE (Groq)
📌 Escribe 'salir' o presiona Ctrl+C para cerrar el agente.
=======================================================

DevOps-Console> en devops-agent crea una carpeta test con un txt dentro que diga Make by AI

💬 Usuario pide: '...'
🧠 Pensando...
🤔 Pensamiento de la IA: Se requiere una acción de escritura en el sistema de archivos. Uso herramienta_CLI.
🛠️ Herramienta seleccionada: herramienta_CLI
💻 Comando asignado: New-Item -ItemType Directory -Name 'test'; Set-Content -Path 'test/test.txt' -Value 'Make by AI'

🛑 [FRENO DE MANO ACTIVADO] Esperando aprobación en Telegram...
🟢 [AUTORIZADO] Permitido desde Telegram. Procediendo a la ejecución...
🚀 Ejecutando comando en el sistema...

Comando ejecutado con éxito.
-------------------------------------------------------

```

---

## 📂 Arquitectura del Proyecto

```text
devops-agent/
│
├── config/
│   └── settings.py          # Gestión y validación de variables de entorno (.env)
│
├── src/
│   ├── agent.py             # Generación y blindaje del System Prompt modular
│   ├── chatops.py           # Pasarela de Webhooks y aprobaciones con la API de Telegram
│   └── tools/               # Módulos de herramientas nativas del agente
│       ├── __init__.py      # Orquestador y mapeo de funciones disponibles
│       ├── system_tools.py  # Scripts de recolección de métricas de hardware
│       ├── docker_tools.py  # Orquestación de infraestructura de contenedores
│       └── global_tools.py  # Wrapper tolerante a encoding (cp1252/utf-8) para CLI
│
└── main.py                  # Loop REPL principal y lógica del pipeline de autorreparación

```

# DISCLAIMER
##########################################################

¡Hola! Soy un desarrollador de software y he creado este agente con fines puramente educativos y de investigación. 
No me hago responsable del mal uso que se le pueda dar a este programa. 
Recuerda que un uso indebido de este agente podría causar daños graves a tu sistema.

El uso de este software corre bajo tu entera responsabilidad.

SOLO ESTA CREADO PARA API EN LA NUBE CON GROQ NO ESTA TESTEADO EN LOCAL NI EN LINUX 
NI EN NINGUN OTRO ENTORNO QUE NO SEA WINDOWS CON GROQ

##########################################################