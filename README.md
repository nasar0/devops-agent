# Autonomous DevOps & SRE AI Agent

Un agente autónomo de Ingeniería de Confiabilidad de Sitios (SRE) y operaciones de desarrollo (DevOps). El sistema está diseñado para ejecutarse de forma híbrida en entornos Windows (PowerShell) y Linux (Bash), interactuando nativamente con el sistema operativo bajo un control de seguridad criptográfica por sesión, memoria contextual integrada y capacidades de autorreparación (Self-Healing) en tiempo real mediante un motor CLI unificado.

---

## Características Principales

* **Cerebro Híbrido:** Capacidad de conmutación entre la nube de alto rendimiento con Groq Cloud (Llama 3.3) y la ejecución local privada mediante Ollama (Llama 3) de forma transparente.
* **Memoria Contextual de Sesión:** Mantiene un historial cíclico vivo de las últimas interacciones de la conversación. Esto permite al agente comprender pronombres, procesar órdenes de seguimiento (ej. *"Modifica su contenido"*) y mantener el hilo conceptual sin pérdida de información entre comandos.
* **Arquitectura CLI Pura y Abstracción:** Autodetecta el sistema operativo anfitrión (Windows o Linux) y traduce las solicitudes directamente en comandos nativos del sistema (como `df -h`, `free -m` o `docker ps -a`), evitando capas intermedias redundantes y adaptando la sintaxis en tiempo real según la terminal destino.
* **Freno de Seguridad con Tokens Únicos:** Clasifica de forma dinámica el nivel de riesgo de cada comando antes de su ejecución. Si detecta acciones de escritura o modificación crítica (crear, borrar, editar archivos o reiniciar servicios), congela el hilo y solicita una aprobación explícita vía Telegram. Utiliza un sistema de Tokens Aleatorios Dinámicos (UUID) por operación para garantizar la integridad de las sesiones.
* **Bucle de Autorreparación (5 Intentos):** Si un comando falla en la terminal, el agente captura el `stderr` y el código de salida nativo, reformula la estrategia recursivamente y realiza hasta 5 intentos de depuración autónoma (explorando directorios si es necesario) antes de reportar el fallo definitivo.
* **Consola Interactiva REPL Optimizada:** Interfaz continua por consola configurada sin buffer de salida de Python (`PYTHONUNBUFFERED=1`), lo que asegura un prompt reactivo e instantáneo tanto en ejecución nativa como dentro de contenedores.

---

## Control de Ejecución Único

El agente traduce las peticiones en lenguaje natural del usuario directamente a comandos del sistema operativo utilizando un único intérprete global evaluado:

| Interfaz / Herramienta | Tipo de Acción | Descripción |
| :--- | :--- | :--- |
| `herramienta_CLI` | Dinámica (Evaluación Estricta) | Intérprete central para cualquier comando nativo del sistema operativo. Determina automáticamente la carga útil, evalúa el flag de peligro (`true/false`) y gestiona el ciclo de vida de la tarea. |

---

## Requisitos e Instalación

### 1. Clonar el repositorio y acceder
```bash
git clone [https://github.com/nasar0/devops-agent.git](https://github.com/nasar0/devops-agent.git)
cd devops-agent

```

### 2. Configuración de Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto para la configuración inicial. Asegúrate de introducir los valores limpios, sin comillas ni espacios residuales:

```env
IA_MODE=cloud
TELEGRAM_TOKEN=tu_api_TELEGRAM_TOKEN
CHAT_ID=tu_CHAT_ID
GROQ_KEY=tu_api_key_de_groq

```

---

## Modos de Despliegue

### Opción A: Despliegue Aislado con Docker (Recomendado)

Para evitar dependencias globales de Python o problemas de entorno, puedes ejecutar el agente dentro de un contenedor aislado que se comunica de forma segura con la máquina anfitriona mediante montajes específicos.

1. **Construir la imagen local:**

```bash
docker build --network=host -t devops-agent .

```

2. **Lanzar el contenedor en segundo plano:**

```bash
docker run -d --name mi-agente-telegram --user root --restart always -v /var/run/docker.sock:/var/run/docker.sock -v /home:/home -e IA_MODE="cloud" -e TELEGRAM_TOKEN="TU_TOKEN" -e CHAT_ID="TU_CHAT_ID" -e GROQ_KEY="TU_GROQ_KEY" devops-agent

```

*(Nota: El flag `--user root` asegura el acceso correcto al socket de Docker y el flag `-v /home:/home` permite que los cambios de archivos impacten directamente en el host real).*

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

---

## Arquitectura del Proyecto

```text
devops-agent/
│
├── config/
│   └── settings.py          # Gestión, tipado estricto y validación Pydantic del .env
│
├── src/
│   ├── agent.py             # Generación del System Prompt modular CLI y conectores de IA (Groq/Ollama)
│   ├── chatops.py           # Pasarela de Webhooks, polling y validación de tokens únicos con Telegram
│   └── tools/               # Módulos de aislamiento de ejecución del agente
│       └── global_tools.py  # Wrapper principal para la ejecución de comandos CLI nativos
│
├── env.example              # Plantilla de referencia para variables de entorno
├── Dockerfile               # Configuración de empaquetado optimizado con cliente Docker nativo
└── main.py                  # Loop REPL principal, gestor de memoria, orquestador CLI e hilo de autorreparación

```

---

## Aviso Legal (Disclaimer)

Este software ha sido desarrollado exclusivamente con fines educativos, de investigación y de automatización controlada de operaciones de desarrollo.

* **Responsabilidad:** El autor no se hace responsable de daños, alteraciones de datos, borrados accidentales o interrupciones de servicio causadas por los comandos ejecutados o sugeridos de forma autónoma por la Inteligencia Artificial.
* **Entorno Seguro:** Se recomienda encarecidamente ejecutar este agente dentro de entornos controlados (Staging), máquinas virtuales o contenedores Docker aislados que tengan los permisos estrictamente limitados en el sistema anfitrión.
 