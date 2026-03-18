from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, status
from typing import Optional, List
from backend.services.media_service import save_multiple, delete_image
from backend.models.room_model import RoomCreate, RoomUpdate
from backend.dependencies.auth import required_admin
from backend.services.room_service import create_room, get_rooms, get_room, update_room, delete_room, create_room_with_images, remove_room_image, add_room_images_to_db, save_multiple

router = APIRouter(prefix="/rooms", tags=["Gestión de Habitaciones"])

# 1. CREAR HABITACIÓN
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(data: RoomCreate, user=Depends(required_admin)):
    # Usamos await porque la DB es asíncrona
    return await create_room(data.model_dump(), user["email"])

# 2. LISTAR HABITACIONES (Público)
@router.get("/")
async def list_rooms(
    page: int = 1,
    limit: int = 10,
    name: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
):
    filters = {"name": name, "active": active}
    return await get_rooms(page, limit, filters)

# 3. VER DETALLE DE HABITACIÓN
@router.get("/{room_id}")
async def get(room_id: str):
    room = await get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return room

# 4. ACTUALIZAR HABITACIÓN
@router.put("/{room_id}")
async def update(room_id: str, data: RoomUpdate, user=Depends(required_admin)):
    updated = await update_room(
        room_id,
        data.model_dump(exclude_unset=True, exclude={"id"}),
        user["email"],
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return updated

# 5. ELIMINAR HABITACIÓN Y SUS IMÁGENES
@router.delete("/{room_id}")
async def delete(room_id: str, user=Depends(required_admin)):
    room = await get_room(room_id)
    if not room:
         raise HTTPException(status_code=404, detail="Habitación no encontrada")
         
    # Borramos imágenes del almacenamiento (Cloudinary o local)
    for image_url in room.get("images", []):
         delete_image(image_url)
        
    await delete_room(room_id)
    return {"message": "Habitación y sus imágenes eliminadas correctamente"}

# 6. CREAR HABITACIÓN CON MÚLTIPLES IMÁGENES (Formulario)
@router.post("/create-with-images")
async def create_room_with_images_router(
    room_number: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    capacity: int = Form(...),
    images: List[UploadFile] = File(...),
    user = Depends(required_admin)
):
    # Procesamos imágenes asíncronamente
    image_urls = save_multiple(images)

    data = {
        "room_number": room_number,
        "name": name,
        "description": description,
        "price": price,
        "capacity": capacity,
    }
    return await create_room_with_images(data, image_urls, user["email"])

# 7. ELIMINAR UNA IMAGEN ESPECÍFICA
@router.delete("/{room_id}/delete-image")
async def delete_room_image(room_id: str, url: str, user=Depends(required_admin)):
    await remove_room_image(room_id, url, user["email"])
    delete_image(url)
    return {"message": "Imagen eliminada con éxito"}


@router.post("/{room_id}/add-images")
async def add_images(room_id: str, files: List[UploadFile] = File(...), user=Depends(required_admin)):
    # 🟢 Usamos save_multiple, que es la que ya existe y funciona bien
    new_urls = save_multiple(files) 
    
    exito = await add_room_images_to_db(room_id, new_urls)
    
    if not exito:
        raise HTTPException(status_code=500, detail="Error al actualizar MongoDB")
        
    return {"message": "Fotos agregadas con éxito", "urls": new_urls}