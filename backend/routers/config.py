from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from backend.db.client import db
from backend.models.config_models import SiteConfig
from backend.schemas.config_schema import site_config_schema
from backend.services.media_service import save_image

# 1. Importamos tu dependencia de seguridad
from backend.dependencies.auth import required_admin

router = APIRouter(prefix="/config", tags=["Configuration"])

# El GET lo dejamos público para que la web pueda cargar el logo y nombre del hotel
@router.get("/")
def get_config():
    config_db = db.settings.find_one({}, {"_id": 0})
    return site_config_schema(config_db)

# 2. Protegemos el PUT agregando dependencies=[Depends(required_admin)]
@router.put("/", dependencies=[Depends(required_admin)])
def update_config(data: SiteConfig):
    db.settings.update_one({}, {"$set": data.dict()}, upsert=True)
    return {"message": "Configuración de Kofán actualizada"}

# 3. Protegemos el POST del logo de la misma manera
@router.post("/logo", dependencies=[Depends(required_admin)])
async def upload_logo(file: UploadFile = File(...)):
    file_url = save_image(file)
    db.settings.update_one({}, {"$set": {"logo_url": file_url}}, upsert=True)
    return {"logo_url": file_url}