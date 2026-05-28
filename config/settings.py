import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Cargar las variables del archivo .env
load_dotenv()

# Definimos el esquema de lo que REQUERIMOS para que el agente funcione
class Settings(BaseModel):
    ia_mode: str = Field(default="LOCAL", alias="IA_MODE")
    groq_key: str = Field(..., alias="GROQ_KEY")
    telegram_token: str = Field(..., alias="TELEGRAM_TOKEN")
    chat_id: str = Field(..., alias="CHAT_ID")

    # Validación extra para asegurarnos de que no metan texto raro en el modo
    @property
    def is_cloud(self) -> bool:
        return self.ia_mode.upper() == "CLOUD"

# Intentar cargar y validar las configuraciones
try:
    config = Settings(
        IA_MODE=os.getenv("IA_MODE"),
        GROQ_KEY=os.getenv("GROQ_KEY"),
        TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN"),
        CHAT_ID=os.getenv("CHAT_ID")
    )
except ValidationError as e:
    print("\n❌ [ERROR DE CONFIGURACIÓN] Faltan variables en el archivo .env:")
    print(e)
    exit(1)