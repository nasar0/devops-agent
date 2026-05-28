import subprocess
import platform

"""
    Ejecuta cualquier comando en la terminal del sistema de forma tolerante a caracteres especiales.
"""
def herramienta_CLI(comando: str, peligro: bool = False) -> str:

    sistema = platform.system()
    print(f"[Global Tool] Ejecutando comando libre en {sistema}: '{comando}'")
    
    try:
        if sistema == "Windows":
            # Usamos encoding cp1252 y errors='ignore' para que la 'ñ' o las tildes de Windows no rompan Python
            resultado = subprocess.run(
                ["powershell", "-Command", comando], 
                capture_output=True, 
                text=True, 
                check=True, 
                encoding="cp1252",
                errors="ignore"
            )
        else:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, check=True)
            
        return resultado.stdout if resultado.stdout else "Comando ejecutado con éxito (Sin salida de texto)."
    except subprocess.CalledProcessError as e:
        # Aquí también aplicamos tolerancia a errores de texto
        stderr_decoded = e.stderr.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore') if isinstance(e.stderr, str) else str(e.stderr)
        return f"❌ Error al ejecutar comando ({e.returncode}):\n{stderr_decoded}"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"