from config.settings import config

def main():
    print("¡Agente DevOps Inicializado Correctamente!")
    print(f"Modo de IA seleccionado: {config.ia_mode}")
    print(f"ID de Telegram cargado: {config.chat_id}")

if __name__ == "__main__":
    main()