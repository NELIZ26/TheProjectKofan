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
    num_cuartos: int = 1
    tipo_camas: str = ""
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
    num_cuartos: Optional[int] = None
    tipo_camas: Optional[str] = None
    amenities: Optional[List[str]] = None

class RoomResponse(RoomBase):
    id: str
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None