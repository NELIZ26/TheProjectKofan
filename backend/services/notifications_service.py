from bson import ObjectId
from datetime import datetime
from backend.db.client import db
from datetime import datetime, timedelta

async def crear_notificacion_panel(user_id: str, titulo: str, mensaje: str, tipo: str = "success", icono: str = "fa-solid fa-circle-check"):
    notificacion = {
        "user_id": ObjectId(user_id),
        "titulo": titulo,
        "mensaje": mensaje,
        "colorTheme": tipo,
        "icono": icono,
        "leida": False,
        "created_at": datetime.utcnow()
    }
    await db.notifications.insert_one(notificacion)

async def get_notificaciones_usuario(user_id: str):
    # Traemos las últimas 20 notificaciones, las más nuevas primero
    cursor = db.notifications.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(20)
    avisos = []
    
    async for doc in cursor:
        fecha_bd = doc.get("created_at")
        
        # 🟢 LÓGICA DE HORA COLOMBIANA Y FORMATO
        if fecha_bd:
            # Le restamos 5 horas a la hora global para que coincida con Colombia
            fecha_colombia = fecha_bd - timedelta(hours=5)
            
            # Formateamos. "%I:%M %p" saca la hora como "08:37 PM"
            # Si en algún momento decides dejar SOLO la fecha, quita el " - %I:%M %p"
            fecha_formateada = fecha_colombia.strftime("%d/%m/%Y - %I:%M %p")
        else:
            fecha_formateada = "Reciente"

        avisos.append({
            "id": str(doc["_id"]),
            "titulo": doc.get("titulo", "Aviso"),
            "mensaje": doc.get("mensaje", ""),
            "colorTheme": doc.get("colorTheme", "success"),
            "icono": doc.get("icono", "fa-solid fa-bell"),
            "leida": doc.get("leida", False),
            "fecha": fecha_formateada # 🟢 La mandamos a Vue lista para mostrarse
        })
    return avisos

async def marcar_todas_leidas_service(user_id: str):
    # Buscamos las que no están leídas de ese usuario y las pasamos a True
    resultado = await db.notifications.update_many(
        {"user_id": ObjectId(user_id), "leida": False},
        {"$set": {"leida": True}}
    )
    return resultado.modified_count