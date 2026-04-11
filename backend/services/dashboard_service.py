from datetime import datetime, timedelta
from backend.db.client import db 

async def get_dashboard_metrics():
    ahora = datetime.utcnow()
    # Primer día del mes actual a las 00:00:00
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. INGRESOS DEL MES (Desde 'invoices')
    pipeline_ingresos = [
        {"$match": {
            "issue_date": {"$gte": inicio_mes},
            "status": "closed" 
        }},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    res_ingresos = await db.invoices.aggregate(pipeline_ingresos).to_list(1)
    ingresos_mes = res_ingresos[0]["total"] if res_ingresos else 0

    # 2. RESERVAS ACTIVAS (Desde 'bookings')
    reservas_activas = await db.bookings.count_documents({
        "estado": "confirmada"
    })

    # 3. HUÉSPEDES HOY (Desde 'bookings')
    # ¡CORREGIDO! Ahora buscamos el estado "ocupada"
    pipeline_huespedes = [
        {"$match": {
            "estado": "ocupada" 
        }},
        {"$project": {
            # Sumamos 1 (el titular) + el tamaño del array de acompañantes
            "total_por_reserva": { 
                "$add": [1, {"$size": {"$ifNull": ["$acompanantes", []]}}] 
            }
        }},
        {"$group": {
            "_id": None,
            "gran_total": {"$sum": "$total_por_reserva"}
        }}
    ]
    
    res_huespedes = await db.bookings.aggregate(pipeline_huespedes).to_list(1)
    huespedes_hoy = res_huespedes[0]["gran_total"] if res_huespedes else 0

    # 4. PORCENTAJE DE OCUPACIÓN REAL
    # Contamos cuántas habitaciones únicas tienen una reserva en estado "ocupada"
    habitaciones_ocupadas = await db.bookings.distinct("habitacion_id", {"estado": "ocupada"})
    # Asumiendo que tu colección de habitaciones se llama 'rooms'
    total_habitaciones = await db.rooms.count_documents({}) 
    
    porcentaje_ocupacion = 0
    if total_habitaciones > 0:
        porcentaje_ocupacion = round((len(habitaciones_ocupadas) / total_habitaciones) * 100)

    # 5. HABITACIONES MÁS SOLICITADAS (Desde 'invoices')
    pipeline_populares = [
        {"$group": {"_id": "$room_name", "conteo": {"$sum": 1}}},
        {"$sort": {"conteo": -1}},
        {"$limit": 3}
    ]
    top_habs = await db.invoices.aggregate(pipeline_populares).to_list(3)
    
    colores = ["success", "primary", "warning"]
    habitaciones_populares = []
    for i, hab in enumerate(top_habs):
        habitaciones_populares.append({
            "nombre": hab["_id"] if hab["_id"] else "Sin nombre",
            "reservas": hab["conteo"],
            "color": colores[i] if i < len(colores) else "info"
        })

    # 6. 🟢 ACTIVIDAD RECIENTE ACTUALIZADA (Últimos 3 movimientos de reservas)
    pipeline_movimientos = [
        # Ordenamos por las últimas reservas creadas o actualizadas
        {"$sort": {"updated_at": -1, "created_at": -1}},
        {"$limit": 3},
        {"$lookup": {"from": "clients", "localField": "cliente_id", "foreignField": "_id", "as": "cliente_info"}},
        {"$unwind": {"path": "$cliente_info", "preserveNullAndEmptyArrays": True}}
    ]
    
    ultimas_reservas = await db.bookings.aggregate(pipeline_movimientos).to_list(3)
    ultimos_movimientos = []
    
    for r in ultimas_reservas:
        cliente = r.get("cliente_info", {})
        nombre_cliente = cliente.get("full_name", r.get("cliente_nombre", "Desconocido"))
        estado_reserva = r.get("estado", "pendiente").capitalize()
        
        # Buscamos la fecha de la última actualización para que el orden sea real
        fecha_mov = r.get("updated_at", r.get("created_at", ahora))
        
        # Ajustamos a la hora de Colombia (-5 horas)
        if fecha_mov.tzinfo:
            fecha_mov = fecha_mov.replace(tzinfo=None)
        fecha_colombia = fecha_mov - timedelta(hours=5)

        ultimos_movimientos.append({
            "id": str(r["_id"]),
            "usuario": nombre_cliente,
            "accion": f"Reserva {estado_reserva}", # 🟢 Muestra el estado real (Ej: Reserva Confirmada)
            "fecha": fecha_colombia.strftime("%d/%m %I:%M %p"), # Formato de 12 horas con AM/PM
            "monto": f"+ ${r.get('monto_total', 0):,}"
        })

    return {
        "stats": {
            "ingresosMes": ingresos_mes,
            "reservasActivas": reservas_activas,
            "huespedesHoy": huespedes_hoy,
            "ocupacionPorcentaje": porcentaje_ocupacion 
        },
        "habitacionesPopulares": habitaciones_populares,
        "ultimosMovimientos": ultimos_movimientos
    }