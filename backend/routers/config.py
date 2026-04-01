from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from backend.db.client import db
from backend.models.config_models import SiteConfig
from backend.schemas.config_schema import site_config_schema
from backend.services.media_service import save_image
from backend.dependencies.auth import required_admin

router = APIRouter(prefix="/config", tags=["Configuration"])

# 1. Agregamos "async" y "await" al GET
@router.get("")
async def get_config():
    # ¡Aquí está la clave! Await le dice a Python que espere a MongoDB
    config_db = await db.settings.find_one({}, {"_id": 0})
    return site_config_schema(config_db)

# 2. Agregamos "async" y "await" al PUT
@router.put("", dependencies=[Depends(required_admin)])
async def update_config(data: SiteConfig):
    # ¡Await también aquí para guardar!
    await db.settings.update_one({}, {"$set": data.dict()}, upsert=True)
    return {"message": "Configuración de Kofán actualizada"}

# 3. El POST ya era async, pero le faltaba el await al guardar en BD
@router.post("/logo", dependencies=[Depends(required_admin)])
async def upload_logo(file: UploadFile = File(...)):
    file_url = save_image(file)
    # ¡Y await aquí también!
    await db.settings.update_one({}, {"$set": {"logo_url": file_url}}, upsert=True)
    return {"logo_url": file_url}