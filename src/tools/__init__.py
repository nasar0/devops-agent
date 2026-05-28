from src.tools.system_tools import check_disk_space, check_cpu_memory
from src.tools.docker_tools import list_docker_containers, restart_container
from src.tools.global_tools import herramienta_CLI  

AVAILABLE_TOOLS = {
    "check_disk_space": check_disk_space,
    "check_cpu_memory": check_cpu_memory,
    "list_docker_containers": list_docker_containers,
    "restart_container": restart_container,
    "herramienta_CLI": herramienta_CLI  
}