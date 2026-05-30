import json
import os
import subprocess

class StatusChecker:
    def __init__(self, config_path="metrics_config.json"):
        self.config_path = config_path

    def load_config(self):
        if not os.path.exists(self.config_path):
            return None
        with open(self.config_path, "r") as f:
            return json.load(f)

    def execute_check(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # Maneja fallos de comandos de forma segura (ej. grep devolviendo vacío sin coincidencia)
            return ""

    def check_system_health(self):
        config = self.load_config()
        if not config:
            return []

        alerts = []
        metrics = config.get("metrics", {})

        # Iteramos dinámicamente sobre cada métrica definida en el archivo de configuración
        for metric_name, data in metrics.items():
            # Si "enabled" es false, saltamos esta métrica directamente
            if not data.get("enabled", False):
                continue

            command = data.get("command")
            alert_msg = data.get("alert_message")
            metric_type = data.get("type", "threshold") # Por defecto asume numérico

            # Inicializamos value vacío para evitar NameError si algo falla
            value = "" 

            # Ejecutamos el comando asociado a la métrica
            try:
                value = self.execute_check(command)
            except Exception as e:
                # En lugar de un print, añadimos el error de ejecución a las alertas que recibirá el usuario por Telegram
                error_telegram = f"❌ **Error de Monitorización SRE**\nFalló la métrica `{metric_name}` al ejecutar el comando.\n⚠️ *Error:* {str(e)}"
                alerts.append(error_telegram)
                continue # Saltamos a la siguiente métrica de forma segura

            # Por umbral numérico (Disco, RAM, CPU...)
            if metric_type == "threshold":
                threshold = data.get("threshold", 100)
                if value.isdigit() and int(value) >= threshold:
                    alerts.append(alert_msg.format(threshold=threshold, value=value))

            # Por salida de texto (Contenedores caídos, procesos muertos...)
            elif metric_type == "output":
                if value: # Si el comando devolvió alguna línea de texto, hay un problema
                    alerts.append(alert_msg.format(value=value))

        return alerts