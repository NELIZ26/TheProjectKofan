from bson import ObjectId

def user_entity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "tipo_persona": user.get("tipo_persona"),
        "full_name": user.get("full_name"),
        "type_document": user.get("type_document"),
        "number_document": user.get("number_document"),
        "email": user.get("email"),
        "country": user.get("country"),  # Campo nuevo
        "city": user.get("city"),        # Campo nuevo
        "phone": user.get("phone"),
        "role": user.get("role", "client"),
        "is_active": user.get("is_active", True),
        "username": user.get("username", user.get("email")) 
    }

#def users_entity(users) -> dict:
 #   return {
  #      "id": str(users.get("_id")),
   #     "name": users.get("names"),
    #    "surnames": users.get("surnames"),
     #   "document_type": users.get("document_type"),
      #  "document_number": users.get("document_number"),
       # "email": users.get("email"),
        #"role": users.get("role"),
        #"disabled": users.get("disabled", False),
        
  #  }
