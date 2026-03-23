

from datetime import datetime, timedelta, timezone
import logging
from backend.db.client import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cancelar_reservas_vencidas():
    logger.info("🤖 Ejecutando revisión automática de reservas vencidas...")
    
    limite_tiempo = datetime.now(timezone.utc) - timedelta(minutes=2)
    
    filtro = {
        "estado": "pendiente",
        "created_at": {"$lt": limite_tiempo}
    }
    
    nuevos_datos = {
        "$set": {
            "estado": "cancelada",
            "motivo_actualizacion": "Cancelación automática: Tiempo de pago agotado (2minutos)",
            "updated_at": datetime.now(timezone.utc),
            "actualizado_por": "Sistema (Bot)"
        }
    }
    
    resultado = await db.bookings.update_many(filtro, nuevos_datos)
    
    if resultado.modified_count > 0:
        logger.info(f"✅ Se cancelaron automáticamente {resultado.modified_count} reservas por falta de pago.")
    else:
        logger.info("✨ Todo al día. Ninguna reserva pendiente ha superado los 2 minutos.")