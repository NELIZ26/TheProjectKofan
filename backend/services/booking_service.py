from backend.db.client import db
from bson import ObjectId
from bson.errors import InvalidId
from backend.schemas.booking_schema import ReservaCreate
from datetime import datetime, timezone
from fastapi import HTTPException, status # Asegúrate de tener estas importaciones


async def create_booking_service(reserva, user_id: str = None):
    # 1. VALIDAR ID Y BUSCAR HABITACIÓN
    try:
        habitacion_obj_id = ObjectId(reserva.habitacion_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="El ID de la habitación no es válido.")

    habitacion = await db.rooms.find_one({"_id": habitacion_obj_id})
    if not habitacion:
        raise HTTPException(status_code=404, detail="La habitación no existe.")

    # 2. PREPARAR LAS FECHAS NUEVAS (En formato UTC para buscar en MongoDB)
    nueva_entrada = datetime.combine(reserva.fecha_entrada, datetime.min.time()).replace(tzinfo=timezone.utc)
    nueva_salida = datetime.combine(reserva.fecha_salida, datetime.min.time()).replace(tzinfo=timezone.utc)

    # 3. EL MOTOR DE DISPONIBILIDAD: Buscar choques de fechas
    # Buscamos si hay alguna reserva activa para esta misma habitación que se cruce en fechas
    reserva_existente = await db.bookings.find_one({
        "habitacion_id": habitacion_obj_id,
        "estado": {"$in": ["pendiente", "confirmada", "ocupada"]}, # Ignoramos las canceladas o finalizadas
        "$and": [
            {"fecha_entrada": {"$lt": nueva_salida}}, 
            {"fecha_salida": {"$gt": nueva_entrada}}   
        ]
    })

    if reserva_existente:
        raise HTTPException(
            status_code=400, 
            detail="Lo sentimos, la habitación ya está reservada durante esas fechas."
        )

    # 4. PREPARAR DICCIONARIO PARA GUARDAR (Si pasó la prueba de fechas)
    reserva_dict = reserva.model_dump() if hasattr(reserva, 'model_dump') else reserva.dict()
    
    # Sobrescribimos las fechas limpias y en UTC
    reserva_dict["fecha_entrada"] = nueva_entrada
    reserva_dict["fecha_salida"] = nueva_salida
    
    if not reserva_dict.get("estado"):
        reserva_dict["estado"] = "pendiente"
        
    reserva_dict["cliente_id"] = ObjectId(user_id) if user_id else None 
    reserva_dict["habitacion_id"] = habitacion_obj_id
    reserva_dict["created_at"] = datetime.now(timezone.utc)

    # 5. GUARDAR LA RESERVA
    result = await db.bookings.insert_one(reserva_dict)
    
    return str(result.inserted_id)

async def update_booking_status_service(reserva_id: str, nuevo_estado: str, motivo: str = None, admin_email: str = None):
    # Preparamos los datos básicos a actualizar
    update_data = {
        "estado": nuevo_estado,
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Si el admin escribió un motivo, lo agregamos al paquete
    if motivo:
        update_data["motivo_actualizacion"] = motivo
        
    # Guardamos quién hizo el cambio para tener un historial limpio
    if admin_email:
        update_data["actualizado_por"] = admin_email
        
    # Ejecutamos la actualización en MongoDB
    result = await db.bookings.update_one(
        {"_id": ObjectId(reserva_id)}, 
        {"$set": update_data}
    )
    
    return result.modified_count > 0


from bson import ObjectId
# Asegúrate de mantener tus otras importaciones arriba (db, datetime, etc.)

async def get_user_bookings_service(user_id: str) -> list:
    """
    Obtiene las reservas de un usuario específico (mis reservas)
    """
    pipeline = [
        {"$match": {"cliente_id": ObjectId(user_id)}},
        {"$lookup": {
            "from": "rooms",
            "localField": "habitacion_id",
            "foreignField": "_id",
            "as": "habitacion_info"
        }},
        {"$unwind": {"path": "$habitacion_info", "preserveNullAndEmptyArrays": True}}
    ]

    cursor = db.bookings.aggregate(pipeline)
    mis_reservas = []

    async for reserva in cursor:
        habitacion = reserva.get("habitacion_info")
        info_habitacion = f"Hab. {habitacion.get('numero_unidad', 'S/N')} - {habitacion.get('tipo', '')}" if habitacion else "Habitación no encontrada"
        
        fecha_ent = reserva.get("fecha_entrada")
        fecha_sal = reserva.get("fecha_salida")

        mis_reservas.append({
            "id": str(reserva["_id"]),
            "habitacion": info_habitacion,
            "habitacion_id": str(reserva.get("habitacion_id", "")),
            "fecha_entrada": fecha_ent.strftime("%Y-%m-%d") if hasattr(fecha_ent, 'strftime') else str(fecha_ent)[:10],
            "fecha_salida": fecha_sal.strftime("%Y-%m-%d") if hasattr(fecha_sal, 'strftime') else str(fecha_sal)[:10],
            "monto_total": reserva.get("monto_total", 0),
            "estado": reserva.get("estado", "pendiente"),
            "observaciones": reserva.get("observaciones", "")
        })
    
    return mis_reservas


async def get_all_bookings_service(estados_filtro: str = None, page: int = 1, limit: int = 10) -> dict:
    """
    Obtiene todas las reservas con soporte para filtros de múltiples estados (pestañas) y paginación.
    """
    pipeline = []
    query_count = {}
    
    # 1. MANEJO DE FILTROS POR ESTADO (Para las pestañas de Vue)
    if estados_filtro:
        lista_estados = estados_filtro.split(",")
        # Filtramos en el pipeline y en el contador
        filtro_match = {"estado": {"$in": lista_estados}}
        pipeline.append({"$match": filtro_match})
        query_count = filtro_match

    # 2. CÁLCULO DE PAGINACIÓN
    skip = (page - 1) * limit
    total_documentos = await db.bookings.count_documents(query_count)
    total_paginas = (total_documentos + limit - 1) // limit if limit > 0 else 1

    # 3. CONSTRUCCIÓN DEL PIPELINE DE AGREGACIÓN
    pipeline.extend([
        {"$sort": {"fecha_entrada": -1}}, # Más recientes primero
        {"$skip": skip},
        {"$limit": limit},
        # Joins con otras colecciones
        {"$lookup": {"from": "rooms", "localField": "habitacion_id", "foreignField": "_id", "as": "habitacion_info"}},
        {"$lookup": {"from": "clients", "localField": "cliente_id", "foreignField": "_id", "as": "cliente_info"}},
        {"$unwind": {"path": "$habitacion_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$cliente_info", "preserveNullAndEmptyArrays": True}}
    ])

    cursor = db.bookings.aggregate(pipeline)
    lista_global = []
    conteo_pendientes = 0

    async for reserva in cursor:
        habitacion = reserva.get("habitacion_info", {})
        cliente = reserva.get("cliente_info", {})
        
        # Contador de pendientes global
        estado = reserva.get("estado", "pendiente")
        if estado == "pendiente":
            conteo_pendientes += 1

        # Lógica de identificación del cliente
        nombre_cliente = cliente.get("full_name", reserva.get("cliente_nombre", "Desconocido"))
        correo_cliente = reserva.get("cliente_email", cliente.get("email", ""))
        celular_cliente = reserva.get("cliente_celular", cliente.get("phone", "")) 

        numero_hab = habitacion.get('room_number', habitacion.get('numero_unidad', 'S/N'))

        lista_global.append({
            "id": str(reserva["_id"]),
            "habitacion_id": str(habitacion.get("_id", "")) if habitacion else None, 
            "cliente": nombre_cliente,
            "cliente_email": correo_cliente,
            "cliente_celular": celular_cliente,
            "tipo_documento": reserva.get("tipo_documento", ""),
            "cliente_documento": reserva.get("cliente_documento", ""),
            "acompanantes": reserva.get("acompanantes", []),
            "consumos_extras": reserva.get("consumos_extras", []),
            "habitacion": f"Hab. {numero_hab}" if habitacion else "N/A",
            "monto": reserva.get("monto_total", 0),
            "estado": estado,
            "fecha_entrada": str(reserva.get("fecha_entrada", "N/A"))[:10],
            "fecha_salida": str(reserva.get("fecha_salida", "N/A"))[:10]
        })

    # Estadísticas globales de ocupación
    habitaciones_ocupadas = await db.rooms.count_documents({"is_available": False})
    total_habitaciones = await db.rooms.count_documents({})

    return {
        "resumen": {
            "total_encontradas": total_documentos, 
            "pendientes_por_aprobar": conteo_pendientes,
            "ocupacion_actual": f"{habitaciones_ocupadas}/{total_habitaciones}",
            "porcentaje_ocupacion": f"{(habitaciones_ocupadas/total_habitaciones)*100:.1f}%" if total_habitaciones > 0 else "0%",
            "total_paginas": total_paginas,        
            "pagina_actual": page                 
        },
        "reservas": lista_global
    }
    

async def update_booking_details_service(reserva_id: str, datos: dict) -> bool:
    try:
        id_obj = ObjectId(reserva_id)
        resultado = await db.bookings.update_one(
            {"_id": id_obj},
            {"$set": datos}
        )
        return resultado.matched_count > 0
    except Exception as e:
        print(f"Error actualizando detalles de reserva: {e}")
        return False