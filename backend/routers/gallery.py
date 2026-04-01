from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Optional
from backend.db.client import db
from bson import ObjectId
from backend.schemas.gallery_schema import images_schema, image_schema
from backend.services.media_service import save_image
from backend.dependencies.auth import required_admin 

router = APIRouter(prefix="/gallery", tags=["Gallery"])

# 1. Modificamos el GET para que pueda recibir un filtro de categoría
@router.get("/")
async def get_gallery(categoria: Optional[str] = None):
    query = {}
    if categoria and categoria != "todos":
        query = {"category": categoria}
        
    cursor = db.gallery.find(query)
    images_db = await cursor.to_list(length=100)
    return images_schema(images_db)

# 2. Modificamos el POST para que reciba el archivo y la categoría como Form()
@router.post("/", dependencies=[Depends(required_admin)])
async def upload_gallery_image(
    file: UploadFile = File(...),
    categoria: str = Form("general") # <-- NUEVO
):
    try:
        file_url = save_image(file)
        # 3. Guardamos la categoría en la base de datos
        new_image = {"url": file_url, "title": file.filename, "category": categoria}
        
        result = await db.gallery.insert_one(new_image)
        inserted_image = await db.gallery.find_one({"_id": result.inserted_id})
        return image_schema(inserted_image)
    except Exception as e:        
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo subir la imagen: " + str(e)
            )
            
@router.delete("/{image_id}", dependencies=[Depends(required_admin)])
async def delete_gallery_image(image_id: str):
    result = await db.gallery.delete_one({"_id": ObjectId(image_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    return {"message": "Imagen eliminada exitosamente"}