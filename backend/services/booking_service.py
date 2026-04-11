from backend.db.client import db
from bson import ObjectId
from bson.errors import InvalidId
from backend.schemas.booking_schema import ReservaCreate
from datetime import datetime, timezone
from fastapi import HTTPException, status 
from backend.services.notifications_service import crear_notificacion_panel


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

# 🟢 Asegúrate de tener este import en la parte superior de tu archivo:
# from backend.services.notifications_service import crear_notificacion_panel

async def update_booking_status_service(reserva_id: str, nuevo_estado: str, motivo: str = None, admin_email: str = None):
    # 🟢 Escudo 1: Aseguramos que el estado sea texto (por si viene de Pydantic Enum)
    estado_str = str(nuevo_estado)

    # Preparamos los datos básicos a actualizar
    update_data = {
        "estado": estado_str,
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
    
    # 🟢 LÓGICA DE NOTIFICACIONES: El "Cartero"
    if result.matched_count > 0:
        # Buscamos la reserva para saber a qué cliente le pertenece
        reserva_actualizada = await db.bookings.find_one({"_id": ObjectId(reserva_id)})
        
        if reserva_actualizada:
            cliente_id = reserva_actualizada.get("cliente_id")
            
            # Solo notificamos si la reserva está vinculada a un usuario registrado (con cuenta)
            if cliente_id:
                # 1. 🟢 VAMOS A BUSCAR EL NOMBRE DE LA HABITACIÓN
                habitacion_id = reserva_actualizada.get("habitacion_id")
                nombre_hab = "nuestras instalaciones" # Plan B seguro
                
                if habitacion_id:
                    try:
                        # Buscamos la cabaña (el str() asegura que no choque si ya era un ObjectId)
                        habitacion = await db.rooms.find_one({"_id": ObjectId(str(habitacion_id))})
                        
                        # Usamos TU lógica perfecta de get_user_bookings_service
                        if habitacion:
                            nombre_oficial = habitacion.get("name")
                            if nombre_oficial:
                                nombre_hab = nombre_oficial
                            else:
                                numero = habitacion.get("room_number", "S/N")
                                tipo = habitacion.get("type", "Cabaña").capitalize()
                                nombre_hab = f"Hab. {numero} - {tipo}"
                    except Exception as e:
                        print(f"Error silencioso al buscar habitación: {e}")

                # 2. 🟢 ARMAMOS LOS MENSAJES
                titulo = "Actualización de Reserva"
                mensaje = f"Tu reserva para '{nombre_hab}' ha cambiado de estado a: {estado_str}."
                tipo = "primary"
                icono = "fa-solid fa-circle-info"
                
                # Personalizamos el mensaje según el estado exacto
                estado_lower = estado_str.lower()
                
                if estado_lower == "confirmada":
                    titulo = "¡Reserva Confirmada!"
                    mensaje = f"Tu estancia en '{nombre_hab}' ha sido aprobada. ¡Te esperamos con los brazos abiertos!"
                    tipo = "success"
                    icono = "fa-solid fa-circle-check"
                    
                elif estado_lower == "ocupada":
                    titulo = "¡Check-in Realizado!"
                    mensaje = f"Tu registro en '{nombre_hab}' fue exitoso. Esperamos que disfrutes al máximo tu descanso en la selva."
                    tipo = "info"
                    icono = "fa-solid fa-house-chimney"
                    
                elif estado_lower == "finalizada":
                    titulo = "¡Check-out Exitoso!"
                    mensaje = f"Tu cuenta de '{nombre_hab}' ha sido cerrada. Gracias por visitarnos, ¡esperamos verte pronto de regreso!"
                    tipo = "secondary"
                    icono = "fa-solid fa-circle-check"
                    
                elif estado_lower == "cancelada":
                    titulo = "Reserva Cancelada"
                    mensaje = f"Tu reserva para '{nombre_hab}' ha sido cancelada. Si crees que esto es un error, por favor contáctanos."
                    tipo = "danger"
                    icono = "fa-solid fa-ban"
                    
                # Disparamos la creación de la notificación en la base de datos
                await crear_notificacion_panel(
                    user_id=str(cliente_id),
                    titulo=titulo,
                    mensaje=mensaje,
                    tipo=tipo,
                    icono=icono
                )
                
    return result.matched_count > 0




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
        
        # 🟢 LÓGICA MEJORADA PARA EL NOMBRE DE LA HABITACIÓN
        if habitacion:
            # 1. Buscamos el nombre (Ej: "Suite Presidencial")
            nombre_oficial = habitacion.get("name")
            
            # 2. Si tiene nombre, lo usamos. Si no, armamos el texto con el número y tipo
            if nombre_oficial:
                info_habitacion = nombre_oficial
            else:
                numero = habitacion.get("room_number", "S/N")
                tipo = habitacion.get("type", "Cabaña").capitalize() # Pone la primera letra en mayúscula
                info_habitacion = f"Hab. {numero} - {tipo}"
        else:
            info_habitacion = "Habitación no encontrada"
            
        fecha_ent = reserva.get("fecha_entrada")
        fecha_sal = reserva.get("fecha_salida")
        fecha_crea = reserva.get("created_at", reserva.get("fecha_creacion")) # Buscamos la fecha de creación

        mis_reservas.append({
            "id": str(reserva["_id"]),
            "habitacion_nombre": info_habitacion, # 🟢 Pasa el nombre correcto a Vue
            "habitacion_id": str(reserva.get("habitacion_id", "")),
            "fecha_entrada": fecha_ent.strftime("%Y-%m-%d") if hasattr(fecha_ent, 'strftime') else str(fecha_ent)[:10],
            "fecha_salida": fecha_sal.strftime("%Y-%m-%d") if hasattr(fecha_sal, 'strftime') else str(fecha_sal)[:10],
            "fecha_creacion": fecha_crea.strftime("%Y-%m-%d") if hasattr(fecha_crea, 'strftime') else str(fecha_crea)[:10],
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
            "fecha_salida": str(reserva.get("fecha_salida", "N/A"))[:10],
            "comprobante_url": reserva.get("comprobante_url", None)
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