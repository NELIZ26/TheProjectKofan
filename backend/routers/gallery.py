from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional
from backend.dependencies.auth import required_admin
from backend.services.gallery_service import get_all_photos, upload_photo, delete_photo

router = APIRouter(prefix="/gallery", tags=["Galería"])


# PÚBLICO: listar fotos con filtro opcional por categoría
@router.get("/")
async def list_photos(categoria: Optional[str] = None):
    return await get_all_photos(categoria)


# ADMIN: subir foto
@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile = File(...),
    titulo: str = Form(...),
    categoria: str = Form(...),
    admin=Depends(required_admin),
):
    return await upload_photo(file, titulo, categoria, admin["email"])


# ADMIN: eliminar foto
@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(photo_id: str, admin=Depends(required_admin)):
    deleted = await delete_photo(photo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    return None