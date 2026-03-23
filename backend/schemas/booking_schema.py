from enum import Enum

from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from pydantic import EmailStr
from datetime import datetime, time, timezone

# Esquema para los acompañantes (se usará dentro de la reserva)

class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    OCUPADA = "ocupada"
    CANCELADA = "cancelada"
    FINALIZADA = "finalizada"

class UpdateEstadoReserva(BaseModel):
        estado: EstadoReserva
        motivo_actualizacion: Optional[str] = None
    
# 2. Estructura de acompañantes (Se mantiene igual)
class AcompananteSchema(BaseModel):
    nombre_completo: str
    numero_documento: str
    parentesco: str # <-- Nuevo campo agregado

# 🟢 2. ESQUEMA BASE CON CAMPOS DE AUDITORÍA
class ReservaBase(BaseModel):
    habitacion_id: str
    fecha_entrada: date
    fecha_salida: date
    monto_total: float
    acompanantes: List[AcompananteSchema] = [] 
    observaciones: Optional[str] = None
    estado: EstadoReserva = EstadoReserva.PENDIENTE
    
    # Buenas prácticas: Definir los campos de seguimiento desde el inicio como opcionales
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    actualizado_por: Optional[str] = None
    motivo_actualizacion: Optional[str] = None

# 🟢 3. ESQUEMA PARA INVITADOS (El que envía tu Vue.js)
class ReservaPublicCreate(ReservaBase):
    tipo_persona: str # "natural" o "juridica"
    tipo_documento: str # "CC", "CE", "PA" o "NIT"
    cliente_documento: str # Cédula o NIT
    cliente_nombre: str # Nombre o Razón social
    cliente_email: str
    cliente_celular: str
# 4. PARA USUARIOS LOGUEADOS: No pide datos de contacto (se sacan del Token)
class ReservaCreate(ReservaBase):
    pass 

# 5. PARA CLIENTES PÚBLICOS: ¡Aquí inyectamos el celular y el correo!
class ReservaPublicCreate(ReservaBase):
    cliente_nombre: str       # Nombre del invitado
    cliente_email: EmailStr    # El correo que pediste (validado)
    cliente_celular: str       # El celular que pediste

# 6. ESQUEMA DE RESPUESTA: Lo que devolvemos al frontend
class ReservaResponse(ReservaBase):
    id: str
    cliente_id: Optional[str] = None # Puede ser nulo si es invitado
    # Si es invitado, también devolvemos sus datos de contacto
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[EmailStr] = None
    cliente_celular: Optional[str] = None

   