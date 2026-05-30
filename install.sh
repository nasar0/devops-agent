#!/bin/bash

# Forzar la ejecución como root (necesario para configurar Systemd)
if [ "$EUID" -ne 0 ]; then
  echo "❌ Por favor, ejecuta este script como root o usando sudo."
  exit 1
fi

echo "🚀 Iniciando la instalación automática del Agente Autónomo DevOps/SRE..."

# 1. Obtener la ruta absoluta actual donde el usuario ha clonado el repositorio
APP_DIR=$(pwd)
echo "[INFO] Directorio de la aplicación detectado en: $APP_DIR"

# 2. Verificar o crear el archivo .env con tus variables exactas
if [ -f "$APP_DIR/.env" ]; then
  echo "[OK] Archivo .env detectado. Respetando configuración existente."
else
  echo "⚠️  No se encontró el archivo .env."
  echo "Creando una plantilla .env con tus variables. Recuerda editarla luego."
  cat <<EOF > "$APP_DIR/.env"
IA_MODE=CLOUD
GROQ_KEY=YOUR_API_KEY_OF_GROQ
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID
EOF
fi

# 3. Verificar o crear la configuración por defecto de métricas SRE
if [ ! -f "$APP_DIR/metrics_config.json" ] && [ -f "$APP_DIR/metrics_config.example.json" ]; then
  echo "[INFO] Creando archivo de configuración metrics_config.json por defecto..."
  cp "$APP_DIR/metrics_config.example.json" "$APP_DIR/metrics_config.json"
fi

# 4. Crear el entorno virtual de Python e instalar dependencias si no existe 
if [ ! -d "$APP_DIR/venv" ]; then
  echo "[INFO] Creando entorno virtual de Python (venv)..."
  python3 -m venv "$APP_DIR/venv"
fi

echo "[INFO] Actualizando herramientas esenciales de pip..."
"$APP_DIR/venv/bin/pip" install --upgrade pip setuptools wheel

echo "[INFO] Instalando dependencias de Python..."
# Forzamos compatibilidad de Rust/PyO3 para entornos modernos como Python 3.13
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
"$APP_DIR/venv/bin/pip" install --no-cache-dir -r "$APP_DIR/requirements.txt"

# 5. Generar dinámicamente el archivo del servicio de Systemd
SERVICE_FILE="/etc/systemd/system/devops-agent.service"
echo "[INFO] Configurando el proceso nativo en Linux ($SERVICE_FILE)..."

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Agente Autónomo DevOps/SRE - Bot de Telegram
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python -u main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=devops-agent

[Install]
WantedBy=multi-user.target
EOF

# 6. Recargar y activar el daemon del sistema operativo
echo "[INFO] Registrando y habilitando el servicio en Systemd..."
systemctl daemon-reload
systemctl enable devops-agent.service

# ==========================================
# 🚀 ¡EL CAMBIO AQUÍ! ARRANCAR INMEDIATAMENTE
# ==========================================
echo "[INFO] Arrancando el proceso nativo automáticamente..."
systemctl start devops-agent.service

echo "===================================================="
echo "✅ ¡TODO COMPLETADO Y ARRANCADO CON ÉXITO!"
echo "===================================================="
echo "El agente YA está ejecutándose en segundo plano como proceso de Linux."
echo ""
echo "⚙️  Si necesitas editar tus tokens: $APP_DIR/.env (Aplica con: sudo systemctl restart devops-agent)"
echo "📊 Para monitorizar los logs en vivo: sudo journalctl -u devops-agent -f"
echo "===================================================="