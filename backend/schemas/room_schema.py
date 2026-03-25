def room_schema(room: dict) -> dict:
    return {
        "id": str(room.get("_id", "")),
        "room_number": room.get("room_number"),
        "name": room.get("name", "Sin nombre"),
        "capacity": room.get("capacity", 1),
        "description": room.get("description", ""),
        "price": room.get("price", 0.0),
        "is_available": room.get("is_available", True), 
        "images": room.get("images", []),
        "main_image": room.get("main_image"),
        "active": room.get("active", True),
        "created_by": room.get("created_by"),
        "updated_by": room.get("updated_by"),
        "created_at": room.get("created_at"),
        "updated_at": room.get("updated_at"),
        "type": room.get("type", "cabana"),
        "amenities": room.get("amenities", []),
    }

def rooms_schema(rooms: list) -> list:
    return [room_schema(r) for r in rooms]