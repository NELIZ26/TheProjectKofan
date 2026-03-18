def room_schema(room) -> dict:
    return {
        "id": str(room["_id"]),
        "room_number": room.get("room_number"),
        "name": room["name"],
        "capacity": room.get("capacity"),
        "description": room.get("description"),
        "price": room["price"],
        "is_available": room.get("is_available", True), 
        "images": room.get("images", []),
        "main_image": room.get("main_image"),
        "active": room.get("active", True),
        "created_by": room.get("created_by"),
        "updated_by": room.get("updated_by"),
        "created_at": room.get("created_at"),
        "updated_at": room.get("updated_at"),
    }

def rooms_schema(rooms):
    return [room_schema(r) for r in rooms]