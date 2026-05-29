# Autonomous DevOps & SRE AI Agent

Un agente autónomo de Ingeniería de Confiabilidad de Sitios (SRE) y operaciones de desarrollo (DevOps). El sistema está diseñado para ejecutarse de forma híbrida en entornos Windows (PowerShell) y Linux (Bash), interactuando nativamente con el sistema operativo bajo un control de seguridad criptográfica por sesión, memoria contextual integrada y capacidades de autorreparación (Self-Healing) en tiempo real.

---

## Características Principales

* **Cerebro Híbrido:** Capacidad de conmutación entre la nube de alto rendimiento con Groq Cloud (Llama 3.3) y la ejecución local privada mediante Ollama (Llama 3) de forma transparente.
* **Memoria Contextual de Sesión:** Mantiene un historial cíclico vivo de las últimas interacciones de la conversación. Esto permite al agente comprender pronombres, procesar órdenes de seguimiento (ej. *"Modifica su contenido"*) y mantener el hilo conceptual sin pérdida de información entre comandos.
* **Abstracción del Entorno:** Autodetecta el sistema operativo anfitrión (Windows o Linux) y adapta la sintaxis de los comandos en tiempo real, evitando conflictos de operadores, formateos incorrectos de rutas o la conversión de comandos encadenados a los estándares de cada terminal.
* **Freno de Seguridad con Tokens Únicos:** Clasifica el nivel de riesgo de cada comando antes de su ejecución. Si detecta acciones de escritura o modificación crítica, congela el hilo y solicita una aprobación explícita vía Telegram. Utiliza un sistema de Tokens Aleatorios Dinámicos (UUID) por operación, garantizando que el bot ignore respuestas residuales o interacciones huérfanas del pasado.
* **Bucle de Autorreparación (5 Intentos):** Si un comando falla en la terminal, el agente captura el `stderr` y el código de salida nativo, reformula la estrategia recursivamente y realiza hasta 5 intentos de depuración autónoma (explorando directorios si es necesario) antes de reportar el fallo definitivo.
* **Consola Interactiva REPL Optimizada:** Interfaz continua por consola configurada sin buffer de salida de Python (`PYTHONUNBUFFERED=1`), lo que asegura un prompt reactivo e instantáneo tanto en ejecución nativa como dentro de contenedores.

---

## Herramientas Integradas

El agente traduce las peticiones en lenguaje natural del usuario en llamadas a funciones estructuradas o ejecuciones en el sistema:

| Herramienta | Tipo de Acción | Descripción |
| :--- | :--- | :--- |
| `check_disk_space` | Lectura / Diagnóstico | Monitoreo multiplataforma del espacio en los discos del sistema. |
| `check_cpu_memory` | Lectura / Diagnóstico | Muestreo de consumos de memoria RAM y CPU en tiempo real. |
| `list_docker_containers` | Lectura / Diagnóstico | Listado y mapeo de infraestructura y contenedores Docker activos. |
| `restart_container` | Escritura (Crítica) | Reinicio controlado de microservicios por nombre de contenedor. |
| `herramienta_CLI` | Dinámica (Evaluada) | Intérprete genérico para cualquier comando nativo del sistema operativo. |

---

## Requisitos e Instalación

### 1. Clonar el repositorio y acceder
```bash
git clone [https://github.com/tu-usuario/devops-agent.git](https://github.com/tu-usuario/devops-agent.git)
cd devops-agent

```

### 2. Configuración de Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto para la configuración inicial. Asegúrate de introducir los valores limpios, sin comillas ni espacios:

```env
IA_MODE=cloud
TELEGRAM_TOKEN=tu_api_TELEGRAM_TOKEN
CHAT_ID=tu_CHAT_ID
GROQ_KEY=tu_api_key_de_groq

```

---

## Modos de Despliegue

### Opción A: Despliegue Aislado con Docker (Recomendado)

Para evitar dependencias globales de Python o problemas de falta de espacio, puedes empaquetar y ejecutar el agente dentro de un contenedor aislado que se comunica de forma segura con el motor del host.

1. **Construir la imagen local:**

```bash
docker build --network=host -t devops-agent .

```

2. **Lanzar el contenedor en segundo plano:**

```bash
docker run -d --name mi-agente-telegram --restart always -v /var/run/docker.sock:/var/run/docker.sock -e IA_MODE="cloud" -e TELEGRAM_TOKEN="TU_TOKEN" -e CHAT_ID="TU_CHAT_ID" -e GROQ_KEY="TU_GROQ_KEY" devops-agent

```

3. **Inspeccionar el estado y los logs en tiempo real:**

```bash
docker logs -f mi-agente-telegram

```

### Opción B: Ejecución Nativa (Entorno Virtual)

1. **Crear e inicializar el entorno virtual:**

```bash
# Crear entorno
python -m venv venv

# Activar en Windows (PowerShell)
.\venv\Scripts\activate

# Activar en Linux (Bash)
source venv/bin/activate

```

2. **Instalar dependencias y arrancar:**

```bash
pip install -r requirements.txt
python main.py

```


## Arquitectura del Proyecto

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
├── Dockerfile               # Configuración de empaquetado optimizado con cliente Docker nativo
└── main.py                  # Loop REPL principal, gestor de memoria e hilo de autorreparación

```

## Aviso Legal (Disclaimer)

Este software ha sido desarrollado exclusivamente con fines educativos, de investigación y de automatización controlada de operaciones de desarrollo.

* **Responsabilidad:** El autor no se hace responsable de daños, alteraciones de datos, borrados accidentales o interrupciones de servicio causadas por los comandos ejecutados o sugeridos de forma autónoma por la Inteligencia Artificial.
* **Entorno Seguro:** Se recomienda encarecidamente ejecutar este agente dentro de entornos controlados (Staging), máquinas virtuales o contenedores Docker aislados que tengan los permisos estrictamente limitados en el sistema anfitrión.
