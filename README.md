# 🤖 Autonomous DevOps & SRE AI Agent

Un agente autónomo avanzado de Ingeniería de Confiabilidad de Sitios (SRE) y operaciones de desarrollo (DevOps). Diseñado para ejecutarse de forma híbrida en entornos **Windows (PowerShell)** y **Linux (Bash)**, interactuando nativamente con el sistema operativo bajo un estricto control de seguridad criptográfica por sesión, memoria contextual avanzada y capacidades de autorreparación (Self-Healing) en tiempo real.

---

## 🚀 Características Principales

* **🧠 Cerebro Híbrido Avanzado:** Capaz de conmutar entre la nube de alto rendimiento con **Groq Cloud (Llama 3.3)** y ejecución local 100% privada mediante **Ollama (Llama 3)** de forma transparente.
* **👁️ Memoria Contextual de Sesión:** Mantiene un historial cíclico vivo de las últimas 10 interacciones de la conversación. Esto permite al agente comprender pronombres, responder a órdenes de seguimiento (ej. *"Modifica su contenido"*) y mantener el hilo sin amnesia entre comandos.
* **💻 Abstracción Automática del Entorno:** Autodetecta el sistema operativo anfitrión (`Windows` o `Linux`). Adapta la sintaxis de los comandos en tiempo real evitando conflictos entre operadores (como el formateo estricto de rutas o la conversión de comandos encadenados `&&` a `;` en entornos Windows).
* **🛡️ Freno de Mano Blindado con Tokens Únicos:** Clasifica de forma autónoma el riesgo de cada comando. Si detecta acciones de escritura o modificación, congela el hilo y solicita aprobación vía Telegram. Utiliza un sistema de **Tokens Aleatorios Dinámicos (UUID)** por sesión, garantizando que el bot ignore respuestas residuales o pulsaciones huérfanas del pasado.
* **🔄 Bucle de Autorreparación Extendido (5 Intentos):** Si un comando CLI falla en la terminal, el agente captura de forma silenciosa el `stderr` y el código de salida nativo, reformula la estrategia recursivamente y realiza hasta **5 intentos de depuración autónoma** (explorando directorios con `pwd` o `ls` si es necesario) antes de reportar un fallo.
* **📟 Consola Interactiva REPL Optimizada:** Interfaz continua por consola configurada sin buffer de salida de Python (`PYTHONUNBUFFERED=1`), asegurando un prompt reactivo e instantáneo al interactuar de forma nativa o mediante contenedores Docker.

---

## 🛠️ Herramientas Integradas

El agente mapea el lenguaje natural del usuario y lo transforma en llamadas a funciones estructuradas o comandos globales:

| Herramienta | Tipo de Acción | Descripción |
| :--- | :--- | :--- |
| `check_disk_space` | Lectura / Diagnóstico | Monitoreo multiplataforma del espacio en discos del sistema. |
| `check_cpu_memory` | Lectura / Diagnóstico | Muestreo de consumos de memoria RAM y CPU en tiempo real. |
| `list_docker_containers` | Lectura / Diagnóstico | Listado y mapeo de infraestructura y contenedores Docker activos. |
| `restart_container` | Escritura (**Crítica**) | Reinicio controlado de microservicios por nombre de contenedor. |
| `herramienta_CLI` | Dinámica (**Evaluada**) | Intérprete genérico para cualquier comando nativo del sistema operativo. |

---

## 📦 Requisitos e Instalación

### 1. Clonar el repositorio y acceder
```bash
git clone [https://github.com/tu-usuario/devops-agent.git](https://github.com/tu-usuario/devops-agent.git)
cd devops-agent

```

### 2. Configurar el Entorno Virtual (Venv) e Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows (PowerShell)
.\venv\Scripts\activate

# Activar en Linux (Bash)
source venv/bin/activate

# Instalar requerimientos estructurados
pip install -r requirements.txt

```

### 3. Configuración de Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto basándote en el archivo `env.example`:

```env
IA_MODE=CLOUD        # CLOUD o LOCAL
GROQ_KEY=gsk_...     # Tu API Key de Groq Cloud
TELEGRAM_TOKEN=...   # Token oficial de tu Bot de Telegram
CHAT_ID=...          # ID del chat con tu Administrador SRE

```

---

## 🕹️ Modo de Uso y Despliegue

### Ejecución Nativa

Para lanzar la consola interactiva infinita del agente SRE en tu máquina local o servidor:

```bash
python main.py

```

### Ejecución Aislada con Docker (Recomendado)

El proyecto incluye soporte para desplegarse dentro de un contenedor Docker manteniendo la entrada estándar interactiva sincronizada y en tiempo real:

```bash
# Construir y levantar el agente en segundo plano
docker compose up -d --build

# Conectarse a la consola interactiva instantánea del agente sin congelamientos de buffer
docker exec -it devops-agent-live python main.py

```

---

## 📂 Arquitectura del Proyecto

```text
devops-agent/
│
├── config/
│   └── settings.py          # Gestión, tipado estricto y validación Pydantic del .env
│
├── src/
│   ├── agent.py             # Generación del System Prompt modular y conectores de IA
│   ├── chatops.py           # Pasarela de Webhooks, polling y validación de tokens únicos con Telegram
│   └── tools/               # Módulos de aislamiento de herramientas del agente
│       ├── __init__.py      # Orquestador principal y mapeo de llamadas autorizadas
│       ├── system_tools.py  # Scripts de recolección de métricas de hardware del Host
│       ├── docker_tools.py  # Control de infraestructura y estado de contenedores
│       └── global_tools.py  # Wrapper tolerante a encodings de sistema (cp1252/utf-8) para CLI
│
├── env.example              # Plantilla de referencia para variables de entorno
├── Dockerfile               # Configuración de empaquetado optimizado sin buffers de terminal
├── docker-compose.yml       # Orquestador del contenedor con montajes de sockets de Docker
└── main.py                  # Loop REPL principal, gestor de memoria e hilo de autorreparación

```

---

## ⚠️ Aviso Legal (Disclaimer)

Este software ha sido desarrollado exclusivamente con fines educativos, de investigación y de automatización controlada de operaciones de desarrollo.

* **Responsabilidad:** El autor no se hace responsable de daños, alteraciones de datos, borrados accidentales o interrupciones de servicio causadas por los comandos ejecutados o sugeridos de forma autónoma por la Inteligencia Artificial.
* **Entorno Seguro:** Se recomienda encarecidamente ejecutar este agente dentro de entornos controlados (Staging), máquinas virtuales o contenedores Docker aislados que tengan los permisos estrictamente limitados en el sistema anfitrión.
