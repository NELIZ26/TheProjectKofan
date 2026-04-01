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
    is_active: bool = True
    role: str = "client"

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
    type_document: Optional[str] = None 