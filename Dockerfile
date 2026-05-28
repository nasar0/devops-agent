# 1. Usamos una imagen oficial de Python ligera basada en Linux
FROM python:3.11-slim

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos solo el archivo de requerimientos primero (para optimizar la caché de Docker)
COPY requirements.txt .

# 4. Instalamos las dependencias directamente en el contenedor (aquí ya no hace falta venv)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto del código del proyecto al contenedor
COPY . .
ENV PYTHONUNBUFFERED=1

# 6. Comando por defecto al arrancar el contenedor
# Usamos -u para que los prints en consola salgan en tiempo real sin retrasos
CMD ["python", "-u", "main.py"]