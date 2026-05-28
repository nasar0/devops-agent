from config.settings import config
from src.tools.system_tools import check_disk_space, check_cpu_memory
from src.tools.docker_tools import list_docker_containers, restart_container

# Diccionario para mapear las funciones del agente
AVAILABLE_TOOLS = {
    "check_disk_space": check_disk_space,
    "check_cpu_memory": check_cpu_memory,
    "list_docker_containers": list_docker_containers,
    "restart_container": restart_container
}

def main():
    print("🚀 ¡Agente DevOps Inicializado Correctamente!")
    print(f"Modo de IA: {config.ia_mode}\n")
    
    print("--- Testeando Herramientas de Consola (CLI Tools) ---")
    
    # Probamos una herramienta de lectura (Inofensiva)
    print("\n[Ejecutando: check_disk_space]")
    print(AVAILABLE_TOOLS["check_disk_space"]())
    
    # Probamos una herramienta de acción (Peligrosa)
    print("\n[Ejecutando: restart_container para 'nginx-proxy']")
    print(AVAILABLE_TOOLS["restart_container"]("nginx-proxy"))

if __name__ == "__main__":
    main()