from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    tipo_persona: str
    full_name: str
    type_document: str
    number_document: str
    email: EmailStr
    country: str   
    city: str 
    password: str
    phone: Optional[str] = None
    role: str = "client"


    
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Esquema para la respuesta de datos del usuario (sin password)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class AdminUserUpdate(UserUpdate):
    role: Optional[str] = None
    number_document: Optional[str] = None
    tipo_persona: Optional[str] = None 

class UserResponse(BaseModel):
    full_name: str
    email: EmailStr
    role: str
