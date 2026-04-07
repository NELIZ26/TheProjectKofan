from datetime import datetime
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

    # 6. ACTIVIDAD RECIENTE (Últimas 3 facturas generadas)
    ultimas_facturas = await db.invoices.find().sort("issue_date", -1).limit(3).to_list(3)
    ultimos_movimientos = []
    for f in ultimas_facturas:
        ultimos_movimientos.append({
            "id": str(f["_id"]),
            "usuario": f.get("guest_name", "Cliente"),
            "accion": "Factura Generada",
            "fecha": f["issue_date"].strftime("%d/%m %H:%M") if "issue_date" in f else "Reciente",
            "monto": f"+ ${f.get('total_amount', 0):,}"
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