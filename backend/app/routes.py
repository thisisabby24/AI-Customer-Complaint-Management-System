from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Complaint

from app.schemas import (
    ComplaintCreate,
    ComplaintText
)

from app.ai_service import (
    extract_complaint
)

from app.complaint_graph import (
    complaint_graph
)

from app.pdf_service import (
    extract_text_from_pdf
)


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"]
)


# =========================================
# HELPER
# Convert date strings to Python date
# =========================================

def parse_date(value):

    if not value:
        return None

    if hasattr(value, "year"):
        return value

    possible_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y"
    ]

    for date_format in possible_formats:

        try:

            return datetime.strptime(
                value,
                date_format
            ).date()

        except ValueError:
            continue

    raise ValueError(
        f"Unable to parse date: {value}"
    )


# =========================================
# DATABASE TEST
# =========================================

@router.get("/test")
def test_complaints(
    db: Session = Depends(get_db)
):

    count = db.query(
        Complaint
    ).count()

    return {
        "message":
            "Complaint database is connected",

        "complaint_count":
            count
    }


# =========================================
# GET ALL COMPLAINTS
# QMS COMPLAINT LEDGER
# =========================================

@router.get("/")
def get_complaints(
    db: Session = Depends(get_db)
):

    try:

        complaints = (
            db.query(Complaint)
            .order_by(
                Complaint.id.desc()
            )
            .all()
        )

        result = []

        for complaint in complaints:

            result.append({

                "id":
                    complaint.id,

                "complaint_source":
                    complaint.complaint_source,

                "customer_name":
                    complaint.customer_name,

                "product_name":
                    complaint.product_name,

                "product_strength":
                    complaint.product_strength,

                "batch_number":
                    complaint.batch_number,

                "affected_quantity":
                    complaint.affected_quantity,

                "manufacturing_date":
                    str(
                        complaint.manufacturing_date
                    )
                    if complaint.manufacturing_date
                    else None,

                "expiry_date":
                    str(
                        complaint.expiry_date
                    )
                    if complaint.expiry_date
                    else None,

                "complaint_date":
                    str(
                        complaint.complaint_date
                    )
                    if complaint.complaint_date
                    else None,

                "complaint_type":
                    complaint.complaint_type,

                "complaint_description":
                    complaint.complaint_description,

                "severity":
                    complaint.severity,

                "priority":
                    complaint.priority,

                "risk_category":
                    complaint.risk_category,

                "risk_score":
                    complaint.risk_score,

                "risk_assessment":
                    complaint.risk_assessment,

                "suggested_action":
                    complaint.suggested_action,

                "status":
                    complaint.status,

                "created_at":
                    complaint.created_at.isoformat()
                    if complaint.created_at
                    else None,

                "updated_at":
                    complaint.updated_at.isoformat()
                    if complaint.updated_at
                    else None

            })

        return {

            "count":
                len(result),

            "complaints":
                result

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# UPDATE COMPLAINT STATUS
# =========================================

@router.put("/{complaint_id}/status")
def update_complaint_status(

    complaint_id: int,

    status: str,

    db: Session = Depends(get_db)

):

    allowed_statuses = [

        "PENDING_TRIAGE",

        "UNDER_INVESTIGATION",

        "CLOSED",

        "REJECTED"

    ]

    status = status.strip().upper()


    if status not in allowed_statuses:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid status. Allowed statuses: "
                + ", ".join(allowed_statuses)
            )

        )


    complaint = (

        db.query(Complaint)

        .filter(
            Complaint.id == complaint_id
        )

        .first()

    )


    if not complaint:

        raise HTTPException(

            status_code=404,

            detail="Complaint not found"

        )


    complaint.status = status

    complaint.updated_at = datetime.now()


    try:

        db.commit()

        db.refresh(complaint)

    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


    return {

        "message":
            "Complaint status updated successfully",

        "complaint_id":
            complaint.id,

        "status":
            complaint.status

    }


# =========================================
# MANUAL COMPLAINT CREATION
# =========================================

@router.post("/")
def create_complaint(

    complaint_data: ComplaintCreate,

    db: Session = Depends(get_db)

):

    try:

        data = complaint_data.model_dump()


        data["manufacturing_date"] = parse_date(
            data.get("manufacturing_date")
        )


        data["expiry_date"] = parse_date(
            data.get("expiry_date")
        )


        data["complaint_date"] = parse_date(
            data.get("complaint_date")
        )


        complaint = Complaint(
            **data
        )


        db.add(complaint)

        db.commit()

        db.refresh(complaint)


        return {

            "message":
                "Complaint created successfully",

            "complaint_id":
                complaint.id

        }


    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================
# AI EXTRACTION ONLY
# =========================================

@router.post("/extract")
def extract_complaint_data(

    complaint_data: ComplaintText

):

    try:

        result = extract_complaint(

            complaint_data.complaint_text

        )


        return {

            "message":
                "Complaint extracted successfully",

            "data":
                result

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================
# COMPLETE AI WORKFLOW
# TEXT → LANGGRAPH → EXTRACTION + RISK
# =========================================

@router.post("/process")
def process_complaint(

    complaint_data: ComplaintText

):

    try:

        result = complaint_graph.invoke({

            "complaint_text":
                complaint_data.complaint_text

        })


        return {

            "message":
                "Complaint processed successfully",

            "extracted_data":
                result["extracted_data"],

            "risk_data":
                result["risk_data"]

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================
# PDF → TEXT → LANGGRAPH
# =========================================

@router.post("/process-pdf")
async def process_pdf_complaint(

    file: UploadFile = File(...)

):

    # -------------------------------------
    # Validate file type
    # -------------------------------------

    if not file.filename:

        raise HTTPException(

            status_code=400,

            detail="No file selected."

        )


    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(

            status_code=400,

            detail="Only PDF files are supported."

        )


    try:

        # ---------------------------------
        # Read uploaded PDF
        # ---------------------------------

        file_bytes = await file.read()


        # ---------------------------------
        # Extract text from PDF
        # ---------------------------------

        complaint_text = extract_text_from_pdf(
            file_bytes
        )


        # ---------------------------------
        # Send extracted text to LangGraph
        # ---------------------------------

        result = complaint_graph.invoke({

            "complaint_text":
                complaint_text

        })


        return {

            "message":
                "PDF complaint processed successfully",

            "filename":
                file.filename,

            "extracted_text":
                complaint_text,

            "extracted_data":
                result["extracted_data"],

            "risk_data":
                result["risk_data"]

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================
# AI WORKFLOW + POSTGRESQL
# =========================================

@router.post("/extract-and-save")
def extract_and_save_complaint(

    complaint_data: ComplaintText,

    db: Session = Depends(get_db)

):

    try:

        # ---------------------------------
        # Run LangGraph
        # ---------------------------------

        result = complaint_graph.invoke({

            "complaint_text":
                complaint_data.complaint_text

        })


        extracted_data = (
            result["extracted_data"]
        )


        risk_data = (
            result["risk_data"]
        )


        # ---------------------------------
        # Combine AI results
        # ---------------------------------

        final_data = {

            **extracted_data,

            **risk_data

        }


        # ---------------------------------
        # Convert dates
        # ---------------------------------

        final_data["manufacturing_date"] = parse_date(
            final_data.get(
                "manufacturing_date"
            )
        )


        final_data["expiry_date"] = parse_date(
            final_data.get(
                "expiry_date"
            )
        )


        final_data["complaint_date"] = parse_date(
            final_data.get(
                "complaint_date"
            )
        )


        # ---------------------------------
        # Save complaint
        # ---------------------------------

        complaint = Complaint(
            **final_data
        )


        db.add(complaint)

        db.commit()

        db.refresh(complaint)


        return {

            "message":
                "Complaint processed and saved successfully",

            "complaint_id":
                complaint.id,

            "extracted_data":
                extracted_data,

            "risk_data":
                risk_data

        }


    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )