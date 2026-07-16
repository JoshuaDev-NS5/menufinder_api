import uuid
import time
from datetime import datetime, timezone


def generate_id(prefix: str = "") -> str:# Genera un ID único con un prefijo opcional
    return f"{prefix}{uuid.uuid4().hex}"


def current_timestamp_ms() -> int:# Devuelve la marca de tiempo actual en milisegundos
    return int(time.time() * 1000)


def current_date_str() -> str:# Devuelve la fecha actual como una cadena
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")