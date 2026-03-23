from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, status
from fastapi.concurrency import run_in_threadpool
from typing import Optional, List
from backend.db.client import db
import uuid
import os
from backend.core.config import UPLOAD_DIR
from backend.services.media_service import save_multiple, delete_image
from backend.models.room_model import RoomCreate, RoomUpdate
from backend.dependencies.auth import required_admin, get_current_user
from pathlib import Path
from backend.services.room_service import (
    create_room, get_rooms, get_room, update_room, 
    delete_room, create_room_with_images, remove_room_image, add_room_images_to_db
)
from backend.schemas.room_schema import room_schema, rooms_schema
from bson import ObjectId

router = APIRouter(prefix="/rooms", tags=["Gestión de Habitaciones"])




# --- ENDPOINTS PÚBLICOS (Para la vista de clientes en Vue) ---
@router.get("/public")
async def get_public_rooms():
    """Retorna solo habitaciones activas y disponibles para los clientes"""
    # Filtramos por las que están activas Y disponibles
    cursor = db.rooms.find({"active": True, "is_available": True}) 
    
    habitaciones = await cursor.to_list(length=100)
    
    # ¡Aquí reutilizas tu función a la perfección!
    return rooms_schema(habitaciones)

@router.get("/public/{room_id}")
async def get_public_room_detail(room_id: str):
    """Detalle de una habitación específica"""
    habitacion = await db.rooms.find_one({
        "_id": ObjectId(room_id), 
        "active": True
    })
    
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada o inactiva")
        
    # ¡Reutilizas tu esquema individual!
    return room_schema(habitacion)


# 1. CREAR HABITACIÓN (Sin imágenes)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(data: RoomCreate, user=Depends(required_admin)):
    return await create_room(data.model_dump(), user["email"])

# 2. LISTAR HABITACIONES
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

# 4. ACTUALIZAR HABITACIÓN (Datos básicos)
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
         
    # 🟢 CORRECCIÓN: Manejo de errores al borrar imágenes para no interrumpir el flujo
    for image_url in room.get("images", []):
        try:
            await run_in_threadpool(delete_image, image_url)
        except Exception as e:
            print(f"Advertencia: No se pudo borrar la imagen {image_url}. Error: {e}")
        
    await delete_room(room_id)
    return {"message": "Habitación y sus imágenes eliminadas correctamente"}

# 6. CREAR HABITACIÓN CON MÚLTIPLES IMÁGENES (Formulario)
@router.post("/create-with-images")
async def create_new_room_with_images(
    room_number: str = Form(...),
    name: str = Form(...),
    price: float = Form(...),
    capacity: int = Form(...),
    description: str = Form(""),
    active: bool = Form(True),
    type: str = Form(), # 🟢 FastAPI atrapa el nuevo campo (por defecto 'cabana' si no viene)
    images: List[UploadFile] = File(...),
    user = Depends(get_current_user) # 🟢 Obtenemos el usuario autenticado
):
    # 1. Armamos el diccionario 'data'
    data = {
        "room_number": room_number,
        "name": name,
        "price": price,
        "capacity": capacity,
        "description": description,
        "active": active,
        "type": type, # 🟢 Lo agregamos al diccionario
    }
    
    # 2. Guardamos las imágenes físicas y creamos la lista de URLs (images)
    image_urls = []
    if images:
        for img in images:
            # Generamos un nombre único
            ext = os.path.splitext(img.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = Path(UPLOAD_DIR) / filename
            
            # Guardamos el archivo en disco
            with open(file_path, "wb") as buffer:
                buffer.write(await img.read())
            
            # Agregamos la ruta relativa a la lista
            image_urls.append(f"/static/uploads/{filename}")

    # 3. Llamamos al servicio EXACTAMENTE con los 3 parámetros que él espera
    return await create_room_with_images(
        data=data, 
        images=image_urls, # Pasamos la lista que acabamos de crear
        user_email=user["email"] # Pasamos el email extraído del token
    )

# 7. ELIMINAR UNA IMAGEN ESPECÍFICA
@router.delete("/{room_id}/delete-image")
async def delete_room_image(room_id: str, url: str, user=Depends(required_admin)):
    await remove_room_image(room_id, url, user["email"])
    # 🟢 CORRECCIÓN: Ejecución segura
    await run_in_threadpool(delete_image, url)
    return {"message": "Imagen eliminada con éxito"}

# 8. AGREGAR IMÁGENES A HABITACIÓN EXISTENTE
@router.post("/{room_id}/add-images")
async def add_images(room_id: str, files: List[UploadFile] = File(...), user=Depends(required_admin)):
    # 🟢 CORRECCIÓN: Ejecución segura
    new_urls = await run_in_threadpool(save_multiple, files) 
    
    exito = await add_room_images_to_db(room_id, new_urls)
    
    if not exito:
        raise HTTPException(status_code=500, detail="Error al actualizar la base de datos")
        
    return {"message": "Fotos agregadas con éxito", "urls": new_urls}


@router.get("/{room_id}/booked-dates")
async def get_booked_dates(room_id: str):
    try:
       
        try:
            id_obj = ObjectId(room_id)
            condicion_id = {"$in": [room_id, id_obj]}
        except:
            condicion_id = room_id 

        query = {
            "habitacion_id": condicion_id,
            "estado": {"$ne": "cancelada"}
        }
        
        cursor = db.bookings.find(query, {"fecha_entrada": 1, "fecha_salida": 1, "_id": 0})
        reservas = await cursor.to_list(length=1000)
        
        return reservas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching booked dates: {str(e)}")