# 1. Imagen base ligera y compatible
FROM python:3.11-slim

# Evita archivos temporales y asegura logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Directorio de trabajo
WORKDIR /opt/devops-agent

# 3. Instalamos curl y dependencias esenciales del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Descargamos SOLO el cliente de Docker (sin servicios ni motores conflictivos)
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz | tar -xz -C /usr/local/bin --strip-components=1 docker/docker

# 5. Copiamos e instalamos los requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el código de la aplicación
COPY . .

# 7. Ejecución por defecto
CMD ["python", "-u", "main.py"]