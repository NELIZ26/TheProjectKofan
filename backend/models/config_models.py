from pydantic import BaseModel
from typing import Optional

class SiteConfig(BaseModel):
    hotel_name: str
    contact_email: str
    phone: str
    address: str
    check_in_time: str
    check_out_time: str
    currency: str
    social_facebook: Optional[str] = ""
    social_instagram: Optional[str] = ""
    social_tiktok: Optional[str] = None
    whatsapp_number: Optional[str] = None
    tax_percentage: float