from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
from datetime import datetime

class ExtraCharge(BaseModel):
    description: str
    amount: float    
    date: datetime = Field(default_factory=datetime.utcnow)

class InvoiceCreate(BaseModel):
    booking_id: str
    guest_name: str
    guest_document: str
    guest_email: str
    guest_phone: str
    room_name: str
    check_in_date: str
    check_out_date: str
    room_subtotal: float
    extra_charges: List[ExtraCharge] = []
    total_amount: float = 0.0
    status: str = "open"  # Puede ser: open, closed, voided
    issue_date: datetime = Field(default_factory=datetime.utcnow)

class AddExtraCharge(BaseModel):
    description: str
    amount: float

class InvoiceSyncUpdate(BaseModel):
    check_out_date: str
    room_subtotal: float
    total_amount: float
    extra_charges: List[Dict[str, Any]] = []