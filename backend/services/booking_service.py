from backend.db.client import db
from bson import ObjectId
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


async def get_user_bookings_service(user_id: str):
    # 1. Buscamos todas las reservas del usuario
    cursor = db.bookings.find({"cliente_id": ObjectId(user_id)})
    
    mis_reservas = []

    # USAMOS UN SOLO BUCLE. Una vez que este bucle termina, el cursor se agota.
    async for reserva in cursor:
        # A. BUSCAMOS LOS DATOS DE LA HABITACIÓN (El "Join" manual)
        habitacion = await db.rooms.find_one({"_id": reserva["habitacion_id"]})
        
        # B. Preparamos el nombre legible (esto lo tenías bien, pero hay que usarlo abajo)
        info_habitacion = f"Hab. {habitacion['numero_unidad']} - {habitacion['tipo']}" if habitacion else "Habitación no encontrada"
    
        # C. CONVERSIÓN MANUAL Y LLENADO DE LA LISTA
        mis_reservas.append({
            "id": str(reserva["_id"]),
            "habitacion": info_habitacion, # <-- Agregamos el nombre legible aquí
            "habitacion_id": str(reserva["habitacion_id"]),
            "fecha_entrada": reserva["fecha_entrada"].strftime("%Y-%m-%d"),
            "fecha_salida": reserva["fecha_salida"].strftime("%Y-%m-%d"),
            "monto_total": reserva["monto_total"],
            "estado": reserva.get("estado", "pendiente"),
            "observaciones": reserva.get("observaciones", "")
        })
    
    return mis_reservas



async def get_all_bookings_service(estado_filtro: str = None):
    # 1. Filtro base
    query = {}
    if estado_filtro:
        query["estado"] = estado_filtro

    # 2. Obtener las reservas
    cursor = db.bookings.find(query).sort("fecha_entrada", -1)
    
    lista_global = []
    # Contadores para el resumen
    conteo_pendientes = 0

    async for reserva in cursor:
        # 1. BUSCAR HABITACIÓN (Usando la llave foránea correcta)
        habitacion = None
        if reserva.get("habitacion_id"):
            habitacion = await db.rooms.find_one({"_id": reserva["habitacion_id"]})
            
        # 2. BUSCAR CLIENTE (Usando la llave foránea correcta)
        cliente = None
        if reserva.get("cliente_id"):
            cliente = await db.clients.find_one({"_id": reserva["cliente_id"]})
        
        # 3. CONTEO DE ESTADOS
        estado = reserva.get("estado", "pendiente")
        if estado == "pendiente":
            conteo_pendientes += 1

        # 4. LÓGICA DEL NOMBRE Y CONTACTO (Soporta usuarios y visitantes públicos)
        nombre_cliente = "Desconocido"
        correo_cliente = ""
        celular_cliente = ""
        
        if cliente: # Si es un usuario registrado, sacamos sus datos base
            nombre_cliente = cliente.get("full_name", "Desconocido")
            correo_cliente = cliente.get("email", "")
            celular_cliente = cliente.get("phone", "") 
        elif reserva.get("cliente_nombre"):
            nombre_cliente = reserva.get("cliente_nombre")
            
        # 🟢 Prioridad a la reserva: Si la reserva trajo un correo/celular específico, lo usamos
        correo_cliente = reserva.get("cliente_email", correo_cliente)
        celular_cliente = reserva.get("cliente_celular", celular_cliente)

        # 5. ARMAR EL DICCIONARIO SEGURO (Agregamos los campos nuevos)
        lista_global.append({
            "id": str(reserva["_id"]),
            "habitacion_id": str(habitacion["_id"]) if habitacion else None, 
            "cliente": nombre_cliente,
            
            # 🟢 AQUÍ ENVIAMOS LOS NUEVOS DATOS A VUE:
            "cliente_email": correo_cliente,
            "cliente_celular": celular_cliente,
            "tipo_documento": reserva.get("tipo_documento", ""),
            "cliente_documento": reserva.get("cliente_documento", ""),
            "acompanantes": reserva.get("acompanantes", []),
            "consumos_extras": reserva.get("consumos_extras", []),
            "habitacion": f"Hab. {habitacion.get('room_number', 'S/N')}" if habitacion else "N/A",
            "monto": reserva.get("monto_total", 0),
            "estado": estado,
            "fecha_entrada": str(reserva.get("fecha_entrada", "N/A"))[:10],
            "fecha_salida": str(reserva.get("fecha_salida", "N/A"))[:10]
        })

    # 3. LÓGICA EXTRA: Contar cuántas habitaciones físicas están ocupadas hoy
    # Esto es independiente de las reservas filtradas
    habitaciones_ocupadas = await db.rooms.count_documents({"is_available": False})
    total_habitaciones = await db.rooms.count_documents({})

    # 4. Devolvemos el "Súper Objeto"
    return {
        "resumen": {
            "total_encontradas": len(lista_global),
            "pendientes_por_aprobar": conteo_pendientes,
            "ocupacion_actual": f"{habitaciones_ocupadas}/{total_habitaciones}",
            "porcentaje_ocupacion": f"{(habitaciones_ocupadas/total_habitaciones)*100:.1f}%" if total_habitaciones > 0 else "0%"
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