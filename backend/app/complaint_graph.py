import json
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.ai_service import (
    extract_complaint,
    client,
    GROQ_MODEL
)


# ============================================================
# COMPLAINT STATE
# ============================================================

class ComplaintState(TypedDict):

    complaint_text: str

    extracted_data: dict

    risk_data: dict


# ============================================================
# NODE 1
# EXTRACT COMPLAINT INFORMATION
# ============================================================

def extract_node(
    state: ComplaintState
):

    print("Running complaint extraction...")

    extracted_data = extract_complaint(
        state["complaint_text"]
    )

    return {
        "extracted_data": extracted_data
    }


# ============================================================
# NODE 2
# ASSESS COMPLAINT RISK
# ============================================================

def risk_node(
    state: ComplaintState
):

    print("Running risk assessment...")

    extracted = state["extracted_data"]

    prompt = f"""
You are a pharmaceutical quality risk assessment assistant.

Analyze the following customer complaint information.

Complaint information:

{json.dumps(
    extracted,
    indent=2
)}

Return ONLY a valid JSON object.

Do NOT return:

- reasoning
- analysis
- markdown
- comments
- ```json
- any text before the JSON
- any text after the JSON

The JSON object MUST contain exactly these fields:

{{
    "severity": "Medium",
    "priority": "Medium",
    "risk_category": "short category",
    "risk_score": 5,
    "risk_assessment": "short assessment",
    "suggested_action": "recommended quality action"
}}

Allowed severity values:

- Minor
- Medium
- Major
- Critical

Allowed priority values:

- Low
- Medium
- High
- Critical

Risk score must be an INTEGER from 0 to 10.

Risk score interpretation:

0-3 = Low
4-6 = Medium
7-8 = High
9-10 = Critical

Consider:

1. Product quality impact
2. Potential patient safety impact
3. Affected quantity
4. Batch information
5. Nature of the complaint
6. Potential efficacy impact
7. Potential safety impact

Important rules:

- Use only information present in the complaint.
- Do not invent facts.
- Do not assume patient harm unless explicitly stated.
- A product quality defect may require investigation even when
  no patient harm is reported.
- Keep the assessment concise.
- Keep the suggested action practical for a pharmaceutical
  quality system.
- Return JSON only.
"""

    response = client.chat.completions.create(

        # IMPORTANT:
        # This must be the model name STRING,
        # not the LangChain ChatGroq object.
        model=GROQ_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        max_completion_tokens=350,

        reasoning_effort="low",

        response_format={
            "type": "json_object"
        }
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:

        raise ValueError(
            "Groq returned an empty risk assessment."
        )

    try:

        risk_data = json.loads(
            content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Groq returned invalid risk JSON: {content}"
        ) from error

    # ========================================================
    # REQUIRED FIELDS
    # ========================================================

    required_fields = [

        "severity",

        "priority",

        "risk_category",

        "risk_score",

        "risk_assessment",

        "suggested_action"

    ]

    for field in required_fields:

        if field not in risk_data:

            risk_data[field] = None

    # ========================================================
    # KEEP ONLY EXPECTED FIELDS
    # ========================================================

    cleaned_risk_data = {

        field: risk_data.get(field)

        for field in required_fields

    }

    # ========================================================
    # CONVERT RISK SCORE TO INTEGER
    # ========================================================

    if cleaned_risk_data["risk_score"] is not None:

        try:

            cleaned_risk_data["risk_score"] = int(
                float(
                    cleaned_risk_data["risk_score"]
                )
            )

        except (
            ValueError,
            TypeError
        ):

            cleaned_risk_data["risk_score"] = None

    # ========================================================
    # LIMIT RISK SCORE TO 0-10
    # ========================================================

    if cleaned_risk_data["risk_score"] is not None:

        cleaned_risk_data["risk_score"] = max(
            0,
            min(
                10,
                cleaned_risk_data["risk_score"]
            )
        )

    return {

        "risk_data": cleaned_risk_data

    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

graph_builder = StateGraph(
    ComplaintState
)


# ============================================================
# ADD NODES
# ============================================================

graph_builder.add_node(
    "extract_complaint",
    extract_node
)

graph_builder.add_node(
    "assess_risk",
    risk_node
)


# ============================================================
# DEFINE GRAPH FLOW
# ============================================================

graph_builder.add_edge(
    START,
    "extract_complaint"
)

graph_builder.add_edge(
    "extract_complaint",
    "assess_risk"
)

graph_builder.add_edge(
    "assess_risk",
    END
)


# ============================================================
# COMPILE GRAPH
# ============================================================

complaint_graph = (
    graph_builder
    .compile()
)