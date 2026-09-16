import os
import json

from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set")

GROQ_MODEL = "openai/gpt-oss-20b"


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# LANGCHAIN MODEL
#
# complaint_graph.py uses this variable.
# ============================================================

model = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="low"
)


# ============================================================
# COMPLAINT EXTRACTION
# ============================================================

def extract_complaint(text: str) -> dict:

    if not text or not text.strip():
        raise ValueError("Complaint text is empty")

    prompt = f"""
Extract information from this pharmaceutical customer complaint.

Use ONLY information explicitly present in the complaint.
If information is missing, return null.
Do not invent information.

Return the requested JSON structure.

Rules:
- Dates must use YYYY-MM-DD.
- risk_score must be an integer from 0 to 10 or null.
- severity must be Minor, Medium, Major, Critical, or null.
- priority must be Low, Medium, High, Critical, or null.
- Keep risk_assessment short.
- Keep suggested_action short.
- complaint_description should contain the actual complaint.
- Return no additional information.

Complaint:
{text}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=1000,
        reasoning_effort="low",
        include_reasoning=False,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "complaint_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "complaint_source": {
                            "type": ["string", "null"]
                        },
                        "customer_name": {
                            "type": ["string", "null"]
                        },
                        "product_name": {
                            "type": ["string", "null"]
                        },
                        "product_strength": {
                            "type": ["string", "null"]
                        },
                        "batch_number": {
                            "type": ["string", "null"]
                        },
                        "affected_quantity": {
                            "type": ["string", "null"]
                        },
                        "manufacturing_date": {
                            "type": ["string", "null"]
                        },
                        "expiry_date": {
                            "type": ["string", "null"]
                        },
                        "complaint_date": {
                            "type": ["string", "null"]
                        },
                        "complaint_type": {
                            "type": ["string", "null"]
                        },
                        "complaint_description": {
                            "type": ["string", "null"]
                        },
                        "severity": {
                            "type": ["string", "null"]
                        },
                        "priority": {
                            "type": ["string", "null"]
                        },
                        "risk_category": {
                            "type": ["string", "null"]
                        },
                        "risk_score": {
                            "type": ["integer", "null"]
                        },
                        "risk_assessment": {
                            "type": ["string", "null"]
                        },
                        "suggested_action": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": [
                        "complaint_source",
                        "customer_name",
                        "product_name",
                        "product_strength",
                        "batch_number",
                        "affected_quantity",
                        "manufacturing_date",
                        "expiry_date",
                        "complaint_date",
                        "complaint_type",
                        "complaint_description",
                        "severity",
                        "priority",
                        "risk_category",
                        "risk_score",
                        "risk_assessment",
                        "suggested_action"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response")

    try:
        result = json.loads(content)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"AI returned invalid JSON: {content}"
        ) from error

    # --------------------------------------------------------
    # Safety cleanup
    # --------------------------------------------------------

    if result.get("risk_score") is not None:
        try:
            score = int(result["risk_score"])
            result["risk_score"] = max(0, min(10, score))
        except (ValueError, TypeError):
            result["risk_score"] = None

    return result


# ============================================================
# SIMPLE RISK ASSESSMENT
# ============================================================

def assess_complaint(text: str) -> dict:
    return extract_complaint(text)


# ============================================================
# COMPLETE COMPLAINT PROCESSING
# ============================================================

def process_complaint(text: str) -> dict:

    result = extract_complaint(text)

    return {
        "extracted_data": result,
        "risk_assessment": {
            "severity": result.get("severity"),
            "priority": result.get("priority"),
            "risk_category": result.get("risk_category"),
            "risk_score": result.get("risk_score"),
            "risk_assessment": result.get("risk_assessment"),
            "suggested_action": result.get("suggested_action")
        }
    }