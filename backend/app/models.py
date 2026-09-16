from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class Complaint(Base):

    __tablename__ = "complaints"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    complaint_source = Column(
        String(100)
    )

    customer_name = Column(
        String(255)
    )

    product_name = Column(
        String(255)
    )

    product_strength = Column(
        String(100)
    )

    batch_number = Column(
        String(100)
    )

    affected_quantity = Column(
        String(100)
    )

    manufacturing_date = Column(
        Date
    )

    expiry_date = Column(
        Date
    )

    complaint_date = Column(
        Date
    )

    complaint_type = Column(
        String(255)
    )

    complaint_description = Column(
        Text
    )

    severity = Column(
        String(50)
    )

    priority = Column(
        String(50)
    )

    risk_category = Column(
        String(255)
    )

    risk_score = Column(
        Integer
    )

    risk_assessment = Column(
        Text
    )

    suggested_action = Column(
        Text
    )

    status = Column(
        String(50),
        default="PENDING_TRIAGE"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )