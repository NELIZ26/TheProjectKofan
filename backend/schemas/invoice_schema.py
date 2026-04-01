def invoice_schema(invoice) -> dict:
    if not invoice:
        return {}
    return {
        "id": str(invoice["_id"]),
        "booking_id": str(invoice.get("booking_id", "")),
        "guest_name": invoice.get("guest_name", ""),
        "guest_document": invoice.get("guest_document", ""),
        "guest_email": invoice.get("guest_email", ""),
        "guest_phone": invoice.get("guest_phone", ""),
        "room_name": invoice.get("room_name", "N/A"),
        "check_in_date": invoice.get("check_in_date", ""),
        "check_out_date": invoice.get("check_out_date", ""),
        "room_subtotal": float(invoice.get("room_subtotal", 0)),
        "extra_charges": invoice.get("extra_charges", []),
        "total_amount": float(invoice.get("total_amount", 0)),
        "status": invoice.get("status", "open"),
        "issue_date": invoice.get("issue_date")
    }

def invoices_schema(invoices) -> list:
    return [invoice_schema(inv) for inv in invoices]