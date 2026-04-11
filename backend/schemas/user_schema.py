from typing import Optional
from pydantic import BaseModel, EmailStr

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserRole(str, Enum):
    ADMIN = "admin"
    RECEPCIONISTA = "recepcionista"
    CLIENT = "client"

class DocumentType(str, Enum):
    CC = "CC"
    CE = "CE"
    PASAPORTE = "PASAPORTE"
    NIT = "NIT"

class UserCreate(BaseModel):
    tipo_persona: str
    full_name: str
    type_document: DocumentType # Usamos Enum
    number_document: str
    email: EmailStr
    country: str   
    city: str 
    password: Optional[str] = None # Opcional para el truco de recepción
    phone: Optional[str] = None
    is_active: bool = True
    role: UserRole = UserRole.CLIENT # Usamos Enum


class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    full_name: str
    email: EmailStr
    role: str

# ==========================================
# 🟢 LÓGICA EMPRESARIAL ESTRICTA (UPDATE)
# ==========================================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None  
    city: Optional[str] = None     

class AdminUserUpdate(UserUpdate):
    tipo_persona: Optional[str] = None 
    type_document: Optional[DocumentType] = None 