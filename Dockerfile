# 1. Usamos una imagen oficial de Python ligera basada en Linux
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc en el disco y asegura salida directa a terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Establecemos el mismo directorio de trabajo que en el servicio de Linux
WORKDIR /opt/devops-agent

# 3. Instalamos el cliente de Docker y curl necesarios para que la IA ejecute comandos CLI nativos
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://get.docker.com | sh \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiamos solo el archivo de requerimientos primero para optimizar la cache de Docker
COPY requirements.txt .

# 5. Instalamos las dependencias directamente en el contenedor
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto del codigo del proyecto al contenedor
COPY . .

# 7. Comando por defecto al arrancar el contenedor en tiempo real
CMD ["python", "-u", "main.py"]