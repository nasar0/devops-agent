import subprocess


# Lista los contenedores Docker activos en el sistema (Válido para Windows y Linux).
def list_docker_containers() -> str:
    try:
        # Este formato limpio funciona en ambas plataformas
        resultado = subprocess.run(["docker", "ps", "--format", "table {{.ID}}\\t{{.Names}}\\t{{.Status}}"], capture_output=True, text=True, check=True)
        return resultado.stdout
    except Exception as e:
        return f"❌ Docker no disponible o apagado: {str(e)}"


# Reinicia un contenedor Docker por su nombre.
def restart_container(container_name: str) -> str:
    try:
        resultado = subprocess.run(["docker", "restart", container_name], capture_output=True, text=True, check=True)
        return f"✅ Contenedor '{container_name}' reiniciado con éxito.\nOutput: {resultado.stdout.strip()}"
    except Exception as e:
        return f"❌ Error al reiniciar el contenedor '{container_name}': {str(e)}"