import subprocess
import platform

#Revisa el espacio en disco del sistema (Compatible con Windows y Linux).
def check_disk_space() -> str:
    sistema = platform.system()
    
    if sistema == "Windows":
        try:
            # Comando de PowerShell para listar discos, tamaño y espacio libre
            cmd = ["powershell", "-Command", "Get-Volume | Select-Object DriveLetter, FileSystemLabel, @{Name='Size(GB)';Expression={'{0:N2}' -f ($_.Size/1GB)}}, @{Name='FreeSpace(GB)';Expression={'{0:N2}' -f ($_.SizeRemaining/1GB)}} | Format-Table"]
            resultado = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
            return f"[WINDOWS HOST - DISCOS]\n{resultado.stdout}"
        except Exception as e:
            return f"Error al leer discos en Windows: {str(e)}"
    
    # --- CÓDIGO PARA UBUNTU SERVER ---
    try:
        resultado = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, check=True)
        return resultado.stdout
    except Exception as e:
        return f"Error al leer el disco en Linux: {str(e)}"


# Revisa el consumo de memoria RAM (Compatible con Windows y Linux).
def check_cpu_memory() -> str:
    sistema = platform.system()
    
    if sistema == "Windows":
        try:
            # Comando de PowerShell para sacar la memoria RAM total y la libre
            cmd = ["powershell", "-Command", "$os = Get-CimInstance Win32_OperatingSystem; $total = [math]::round($os.TotalVisibleMemorySize / 1MB, 2); $libre = [math]::round($os.FreePhysicalMemory / 1MB, 2); $usada = [math]::round($total - $libre, 2); Write-Output 'RAM Total: ' $total 'GB | Usada: ' $usada 'GB | Libre: ' $libre 'GB'"]
            resultado = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
            return f"[WINDOWS HOST - MEMORIA]\n{resultado.stdout.strip()}"
        except Exception as e:
            return f"Error al leer la memoria en Windows: {str(e)}"
            
    # --- CÓDIGO PARA UBUNTU SERVER ---
    try:
        resultado = subprocess.run(["free", "-m"], capture_output=True, text=True, check=True)
        return resultado.stdout
    except Exception as e:
        return f"Error al leer la memoria en Linux: {str(e)}"