# 1. Usamos una versión de Python limpia, ligera y altamente compatible
FROM python:3.11-slim

# Evita la creación de archivos temporales .pyc y fuerza salida directa a consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Definimos el directorio de ejecución dentro del contenedor
WORKDIR /opt/devops-agent

# 3. Instalamos curl y el cliente binario de Docker para poder mandar comandos a la máquina real
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://get.docker.com | sh \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiamos el archivo de requerimientos para instalar las dependencias de forma eficiente
COPY requirements.txt .

# 5. Instalamos todas las librerías de Python sin usar caché para ahorrar espacio
RUN pip install --no-cache-dir -r requirements.txt

# 6. Movemos absolutamente todo tu código, carpetas y configuraciones dentro de la imagen
COPY . .

# 7. Ejecución inmediata del bot al encender el contenedor
CMD ["python", "-u", "main.py"]