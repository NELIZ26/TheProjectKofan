from pydantic import BaseModel
from typing import Optional

# 1. ESQUEMA DE RESPUESTA (Lo que se envía a Vue)
class NotificationResponse(BaseModel):
    id: str
    titulo: str
    mensaje: str
    colorTheme: str
    icono: str
    leida: bool
    fecha: str # Enviamos la fecha ya formateada como string (Ej: "06/04/2026 20:15")

# 2. ESQUEMA DE CREACIÓN (Opcional, por si algún día quieres crear avisos desde Postman o el Admin web)
class NotificationCreate(BaseModel):
    titulo: str
    mensaje: str
    tipo: Optional[str] = "success"
    icono: Optional[str] = "bi-check-circle-fill"