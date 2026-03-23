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


class RoomCreate(RoomBase):
    room_number: str
    name: str
    description: Optional[str] = None
    price: float
    capacity: int
    type : str


class RoomUpdate(BaseModel):
    id: str  # Lo dejamos porque vimos que tu backend lo exige en el body
    room_number: Optional[str] = None # Agregamos este que faltaba
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    capacity: Optional[int] = None    # Cambiamos 'stock' por 'capacity' para que coincida con tu Vue
    images: Optional[List[str]] = None
    main_image: Optional[str] = None
    active: Optional[bool] = None
    type : Optional[str] = None


class RoomResponse(RoomBase):
    id: str
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None