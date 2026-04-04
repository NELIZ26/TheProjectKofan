from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Optional
from backend.services.gallery_service import get_all_photos, upload_photo, delete_photo
from backend.dependencies.auth import required_admin, get_current_user

router = APIRouter(prefix="/gallery", tags=["Gallery"])

@router.get("/")
async def get_gallery(categoria: Optional[str] = None):
    # 🟢 1. DELEGAMOS LA BÚSQUEDA AL SERVICIO
    return await get_all_photos(categoria)

@router.post("/", dependencies=[Depends(required_admin)])
async def upload_gallery_image(
    file: UploadFile = File(...),
    categoria: str = Form("general"),
    user = Depends(get_current_user) # Extraemos el usuario para saber quién subió la foto
):
    try:
        # 🟢 2. DELEGAMOS LA SUBIDA Y CREACIÓN AL SERVICIO
        # Nota: Asumo que el título inicial será el nombre del archivo
        return await upload_photo(file, titulo=file.filename, categoria=categoria, uploader_email=user["email"])
    except Exception as e:        
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo subir la imagen: " + str(e)
            )
            
@router.delete("/{image_id}", dependencies=[Depends(required_admin)])
async def delete_gallery_image(image_id: str):
    # 🟢 3. DELEGAMOS EL BORRADO (Físico y de BD) AL SERVICIO
    exito = await delete_photo(image_id)
    
    if not exito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    
    return {"message": "Imagen y archivo eliminados exitosamente"}