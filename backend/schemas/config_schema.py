def site_config_schema(config) -> dict:
    if not config:
        return {
            "hotel_name": "Kofán Hospedaje",
            "logo_url": "",
            "contact_email": "",
            "phone": "",
            "address": "",
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "currency": "COP",
            "social_facebook": "",
            "social_instagram": "",
            "tax_percentage": 0.0
        }
        
    return {
        "hotel_name": config.get("hotel_name", "Kofán Hospedaje"),
        "logo_url": config.get("logo_url", ""),
        "contact_email": config.get("contact_email", ""),
        "phone": config.get("phone", ""),
        "address": config.get("address", ""),
        "check_in_time": config.get("check_in_time", "15:00"),
        "check_out_time": config.get("check_out_time", "11:00"),
        "currency": config.get("currency", "COP"),
        "social_facebook": config.get("social_facebook", ""),
        "social_instagram": config.get("social_instagram", ""),
        "tax_percentage": config.get("tax_percentage", 0.0)
    }