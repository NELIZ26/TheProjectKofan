# backend/schemas/gallery_schema.py

def image_schema(img) -> dict:
    # Si no hay imagen, devolvemos un diccionario vacío para no romper nada
    if not img:
        return {}
        
    return {
        "id": str(img["_id"]),
        "url": img.get("url", ""),
        "title": img.get("title", ""),
        "categoria": img.get("category", "general")
    }

def images_schema(images) -> list:
    return [image_schema(img) for img in images]