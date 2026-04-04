from fastapi import APIRouter, Depends, UploadFile, File
from backend.models.config_models import SiteConfig
from backend.schemas.config_schema import site_config_schema
from backend.dependencies.auth import required_admin
from backend.services.config_service import get_site_config, update_site_config, update_site_logo


router = APIRouter(prefix="/config", tags=["Configuration"])

@router.get("")
async def get_config():
    config_db = await get_site_config()
    return site_config_schema(config_db)

@router.put("", dependencies=[Depends(required_admin)])
async def update_config(data: SiteConfig):
    # Pasamos los datos validados por Pydantic como diccionario
    return await update_site_config(data.model_dump())

@router.post("/logo", dependencies=[Depends(required_admin)])
async def upload_logo(file: UploadFile = File(...)):
    # Delegamos toda la lógica de guardado y limpieza al servicio
    return await update_site_logo(file)