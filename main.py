from config.settings import config
from src.tools.system_tools import check_disk_space, check_cpu_memory
from src.tools.docker_tools import list_docker_containers, restart_container
from src.chatops import send_telegram_message, request_human_approval

# Diccionario para mapear las funciones del agente
AVAILABLE_TOOLS = {
    "check_disk_space": check_disk_space,
    "check_cpu_memory": check_cpu_memory,
    "list_docker_containers": list_docker_containers,
    "restart_container": restart_container
}

def main():
    print("🚀 ¡Agente DevOps Inicializado!")
    
    # 1. Test de mensaje simple
    print("\n[Enviando saludo a Telegram...]")
    send_telegram_message("🤖 *Agente DevOps Online* listo para la Fase 3.")
    
    # 2. Test del Freno de Mano
    comando_peligroso = "docker restart nginx-proxy"
    
    # Lanza la pregunta al móvil
    aprobado = request_human_approval(comando_peligroso)
    
    if aprobado:
        print("🟢 [ACCION COMPROBADA] Le diste a SÍ. Procediendo a simular la ejecución...")
        send_telegram_message("✅ Ejecutando acción autorizada por el administrador.")
    else:
        print("🔴 [ACCION CANCELADA] Le diste a NO o falló. Frenando ejecución.")
        send_telegram_message("❌ Acción denegada por el administrador.")

if __name__ == "__main__":
    main()