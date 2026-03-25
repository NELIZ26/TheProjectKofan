from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    images: List[str] = []
    main_image: Optional[str] = None
    active: bool = True
    # 🟢 LO SUBIMOS A LA BASE PARA QUE LA RESPUESTA TAMBIÉN LO TENGA
    amenities: List[str] = []

class RoomCreate(RoomBase):
    room_number: str
    capacity: int
    type: str

class RoomUpdate(BaseModel):
    id: str  
    room_number: Optional[str] = None 
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    capacity: Optional[int] = None    
    images: Optional[List[str]] = None
    main_image: Optional[str] = None
    active: Optional[bool] = None
    type: Optional[str] = None
    # 🟢 En el Update sí lo dejamos explícito por si mandan una lista vacía para borrar
    amenities: Optional[List[str]] = None

class RoomResponse(RoomBase):
    id: str
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Como hereda de RoomBase, ¡ya trae amenities incluido!