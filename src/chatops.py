
import time
import requests
from config.settings import config

TELEGRAM_API_URL = f"https://api.telegram.org/bot{config.telegram_token}"

#Envía un mensaje de texto plano a tu Telegram.
def send_telegram_message(text: str):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": config.chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

"""
    [EL FRENO DE MANO]
    Envía un mensaje con botones de Confirmar/Cancelar a Telegram
    y se queda escuchando (Polling) hasta que el usuario pulse un botón.
"""


def request_human_approval(action_details: str, task_token: str) -> bool:
    url_send = f"{TELEGRAM_API_URL}/sendMessage"
    
    # Diseño de los botones interactivos (Inline Keyboard) usando el token unico
    # Cada boton ahora devuelve 'yes_TOKEN' o 'no_TOKEN' como informacion de callback
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Confirmar (SÍ)", "callback_data": f"yes_{task_token}"},
                {"text": "❌ Cancelar (NO)", "callback_data": f"no_{task_token}"}
            ]
        ]
    }
    
    mensaje = (
        f"⚠️ *SOLICITUD DE ACCIÓN CRÍTICA*\n\n"
        f"ID de Tarea: `{task_token}`\n"
        f"El agente DevOps quiere ejecutar:\n"
        f"`{action_details}`\n\n"
        f"¿Autorizas esta acción?"
    )
    
    payload = {
        "chat_id": config.chat_id,
        "text": mensaje,
        "reply_markup": keyboard,
        "parse_mode": "Markdown"
    }
    
    try:
        # Enviamos el mensaje con los botones dinamicos a Telegram
        response = requests.post(url_send, json=payload, timeout=10).json()
        if not response.get("ok"):
            print("❌ Error al enviar la botonera a Telegram.")
            return False
            
        print(f"\n🛑 [FRENO DE MANO ACTIVADO] Esperando aprobación en Telegram para la tarea [{task_token}]...")
        
        # Bucle de espera (Polling continuo)
        url_updates = f"{TELEGRAM_API_URL}/getUpdates"
        offset = None
        
        while True:
            params = {"timeout": 5, "allowed_updates": ["callback_query"]}
            if offset:
                params["offset"] = offset
                
            updates = requests.get(url_updates, params=params, timeout=10).json()
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    # Comprobamos si la actualizacion proviene de una pulsacion de boton
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        respuesta = callback["data"]   
                        msg_id = callback["message"]["message_id"]
                        
                        # FILTRO DE SEGURIDAD CRÍTICO: Comprobamos si la respuesta pertenece al token actual
                        # Si no coincide (es un residuo del pasado), el bucle ignora el evento y sigue esperando
                        if not (respuesta == f"yes_{task_token}" or respuesta == f"no_{task_token}"):
                            continue

                        # Una vez validado el token correspondiente, procedemos a borrar los botones
                        url_edit = f"{TELEGRAM_API_URL}/editMessageReplyMarkup"
                        payload_edit = {
                            "chat_id": config.chat_id,
                            "message_id": msg_id,
                            "reply_markup": {"inline_keyboard": []}
                        }
                        requests.post(url_edit, json=payload_edit, timeout=5)
                        
                        # Retorna True si coincide exactamente con la aprobacion de este token especifico
                        return respuesta == f"yes_{task_token}"
                        
            time.sleep(3) # Pausa controlada para evitar saturacion de la CPU
            
    except Exception as e:
        print(f"❌ Error en el flujo de aprobación: {e}")
        return False