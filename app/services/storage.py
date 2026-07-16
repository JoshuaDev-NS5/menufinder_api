import uuid
from datetime import datetime

import boto3
from botocore.client import Config
from fastapi import UploadFile, HTTPException

from app.core.config import settings
#Tipos de contenido permitidos para las fotos de menú
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

MAX_FILE_SIZE_MB = 8
#Tipo de cliente de boto3 para interactuar con Cloudflare R2, usando las credenciales y configuración del archivo de configuración
_r2_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

# Función para subir una foto de menú a Cloudflare R2
async def upload_menu_photo(file: UploadFile, restaurant_id: str) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Usa JPEG, PNG o WEBP.",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"La imagen supera el límite de {MAX_FILE_SIZE_MB} MB.",
        )

    extension = file.content_type.split("/")[-1]
    # timestamp + uuid en el nombre: evita colisiones y que el CDN sirva
    # una foto vieja en caché cuando el dueño actualiza el menú del día
    timestamp = int(datetime.utcnow().timestamp())
    unique_id = uuid.uuid4().hex[:8]
    key = f"menus/{restaurant_id}/{timestamp}_{unique_id}.{extension}"

    try:
        _r2_client.put_object(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error al subir la imagen a R2: {str(e)}",
        )

    return f"{settings.r2_public_url}/{key}"

# Función para borrar una foto de menú de Cloudflare R2
def delete_menu_photo(photo_url: str) -> None:
    """Borra un objeto de R2 a partir de su URL pública. Se usa cuando
    se elimina un restaurante o se reemplaza la foto de un menú."""
    if not photo_url.startswith(settings.r2_public_url):
        return  # no es una URL nuestra (ej. foto de stock antigua), no tocar

    key = photo_url.replace(f"{settings.r2_public_url}/", "")
    try:
        _r2_client.delete_object(Bucket=settings.r2_bucket_name, Key=key)
    except Exception:
        # no queremos que fallar al borrar la foto tumbe la operación principal
        pass