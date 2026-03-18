from backend.db.client import db
from bson import ObjectId
from backend.schemas.booking_schema import ReservaCreate
from datetime import datetime
from fastapi import HTTPException, status


async def create_booking_service(reserva, user_id: str):
    # 1. Buscar la habitación
    habitacion_obj_id = ObjectId(reserva.habitacion_id)
    habitacion = await db.rooms.find_one({"_id": habitacion_obj_id})

    # 2. Validación de existencia y disponibilidad
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La habitación no existe."
        )

    if not habitacion.get("is_available", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lo sentimos, esta habitación ya se encuentra ocupada o reservada."
        )

    # 3. Preparar el diccionario
    reserva_dict = reserva.model_dump()

    if not reserva_dict.get("estado"):
        reserva_dict["estado"] = "pendiente"

    reserva_dict["fecha_entrada"] = datetime.combine(reserva.fecha_entrada, datetime.min.time())
    reserva_dict["fecha_salida"] = datetime.combine(reserva.fecha_salida, datetime.min.time())
    reserva_dict["habitacion_id"] = habitacion_obj_id

    # cliente_id puede ser None si es reserva pública
    if user_id:
        reserva_dict["cliente_id"] = ObjectId(user_id)
    else:
        reserva_dict["cliente_id"] = None

    # 4. Guardar reserva
    result = await db.bookings.insert_one(reserva_dict)

    # 5. Marcar habitación como ocupada
    await db.rooms.update_one(
        {"_id": habitacion_obj_id},
        {"$set": {"is_available": False}}
    )

    return str(result.inserted_id)


async def update_booking_status_service(reserva_id: str, nuevo_estado: str):
    result = await db.bookings.update_one(
        {"_id": ObjectId(reserva_id)},
        {"$set": {"estado": nuevo_estado}}
    )

    # Si se cancela o finaliza, la habitación queda libre
    if nuevo_estado in ["cancelada", "finalizada"]:
        reserva = await db.bookings.find_one({"_id": ObjectId(reserva_id)})
        if reserva:
            # Corregido: faltaba await
            await db.rooms.update_one(
                {"_id": ObjectId(reserva["habitacion_id"])},
                {"$set": {"is_available": True}}
            )

    return result.modified_count > 0


async def get_user_bookings_service(user_id: str):
    cursor = db.bookings.find({"cliente_id": ObjectId(user_id)})
    mis_reservas = []

    async for reserva in cursor:
        habitacion = await db.rooms.find_one({"_id": reserva["habitacion_id"]})

        # Corregido: usar campos reales del room_schema (name y room_number)
        if habitacion:
            info_habitacion = f"{habitacion.get('name', 'Habitación')} - #{habitacion.get('room_number', '')}"
        else:
            info_habitacion = "Habitación no encontrada"

        mis_reservas.append({
            "id": str(reserva["_id"]),
            "habitacion": info_habitacion,
            "habitacion_id": str(reserva["habitacion_id"]),
            "fecha_entrada": reserva["fecha_entrada"].strftime("%Y-%m-%d"),
            "fecha_salida": reserva["fecha_salida"].strftime("%Y-%m-%d"),
            "monto_total": reserva["monto_total"],
            "estado": reserva.get("estado", "pendiente"),
            "observaciones": reserva.get("observaciones", "")
        })

    return mis_reservas


async def get_all_bookings_service(estado_filtro: str = None):
    query = {}
    if estado_filtro:
        query["estado"] = estado_filtro

    cursor = db.bookings.find(query).sort("fecha_entrada", -1)

    lista_global = []
    conteo_pendientes = 0

    async for reserva in cursor:
        habitacion = await db.rooms.find_one({"_id": reserva["habitacion_id"]})

        # Corregido: buscar en db.clients (colección unificada), no db.users
        cliente_id = reserva.get("cliente_id")
        cliente = await db.clients.find_one({"_id": cliente_id}) if cliente_id else None

        estado = reserva.get("estado", "pendiente")
        if estado == "pendiente":
            conteo_pendientes += 1

        # Corregido: usar room_number en lugar de numero_unidad
        lista_global.append({
            "id": str(reserva["_id"]),
            "cliente": cliente["full_name"] if cliente else reserva.get("cliente_nombre", "N/A"),
            "habitacion": f"Hab. {habitacion.get('room_number', '?')} - {habitacion.get('name', '')}" if habitacion else "N/A",
            "monto": reserva["monto_total"],
            "estado": estado
        })

    habitaciones_ocupadas = await db.rooms.count_documents({"is_available": False})
    total_habitaciones = await db.rooms.count_documents({})

    return {
        "resumen": {
            "total_encontradas": len(lista_global),
            "pendientes_por_aprobar": conteo_pendientes,
            "ocupacion_actual": f"{habitaciones_ocupadas}/{total_habitaciones}",
            "porcentaje_ocupacion": f"{(habitaciones_ocupadas / total_habitaciones) * 100:.1f}%" if total_habitaciones > 0 else "0%"
        },
        "reservas": lista_global
    }