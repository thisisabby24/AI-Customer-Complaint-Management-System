from pydantic import BaseModel


# =========================================
# Complaint Text
# =========================================

class ComplaintText(BaseModel):

    complaint_text: str


# =========================================
# Complaint Creation
# =========================================

class ComplaintCreate(BaseModel):

    complaint_source: str | None = None

    customer_name: str | None = None

    product_name: str | None = None

    product_strength: str | None = None

    batch_number: str | None = None

    affected_quantity: str | None = None

    manufacturing_date: str | None = None

    expiry_date: str | None = None

    complaint_date: str | None = None

    complaint_type: str | None = None

    complaint_description: str | None = None

    severity: str | None = None

    priority: str | None = None

    risk_category: str | None = None

    risk_score: int | float | None = None

    risk_assessment: str | None = None

    suggested_action: str | None = None