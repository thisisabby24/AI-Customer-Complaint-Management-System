import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")


if not api_key:
    raise ValueError("GROQ_API_KEY is not set")


if not model:
    raise ValueError("GROQ_MODEL is not set")


client = Groq(
    api_key=api_key
)


def interpret_assistant_command(
    command: str,
    current_complaint: dict
) -> dict:

    if not command or not command.strip():
        raise ValueError(
            "Assistant command cannot be empty."
        )

    prompt = f"""
You are an AI assistant for a pharmaceutical
Customer Complaint Management System.

The user wants to modify or review complaint
information.

Current complaint data:

{json.dumps(
    current_complaint,
    indent=2
)}

User command:

{command}

Your job is to understand the user's intention.

You can update ONLY these fields:

- complaint_source
- customer_name
- product_name
- product_strength
- batch_number
- affected_quantity
- manufacturing_date
- expiry_date
- complaint_date
- complaint_type
- complaint_description
- severity
- priority
- risk_category
- risk_score
- risk_assessment
- suggested_action

Return ONLY valid JSON.

Use exactly this structure:

{{
    "action": "update",
    "field": "batch_number",
    "value": "AMX240603",
    "message": "Batch number updated to AMX240603."
}}

Possible actions:

"update"
"answer"

Rules:

1. If the user wants to change a complaint field,
   use action "update".

2. Put the exact database/form field name in "field".

3. Put the new value in "value".

4. If the user is asking a question rather than
   changing a field, use action "answer".

5. For an answer, set "field" to null and
   "value" to null.

6. Put the natural-language response in "message".

7. Do not invent information.

8. Do not modify more than one field in a single
   command.

9. Return JSON only.

Examples:

User:
"Change the batch number to AMX240603"

Return:
{{
    "action": "update",
    "field": "batch_number",
    "value": "AMX240603",
    "message": "Batch number updated to AMX240603."
}}

User:
"Change affected quantity to 20 capsules"

Return:
{{
    "action": "update",
    "field": "affected_quantity",
    "value": "20 capsules",
    "message": "Affected quantity updated to 20 capsules."
}}

User:
"Set priority to High"

Return:
{{
    "action": "update",
    "field": "priority",
    "value": "High",
    "message": "Priority updated to High."
}}

User:
"What is the current batch number?"

Return:
{{
    "action": "answer",
    "field": null,
    "value": null,
    "message": "The current batch number is AMX240602."
}}

Return JSON only.
"""

    response = client.chat.completions.create(
        model=model,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        },

        temperature=0,

        max_completion_tokens=250,

        # Groq accepts low/medium/high.
        # "none" is not a valid value.
        reasoning_effort="low",

        include_reasoning=False
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )

    try:

        result = json.loads(
            content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Groq returned invalid JSON: {content}"
        ) from error

    if result.get("action") not in [
        "update",
        "answer"
    ]:

        raise ValueError(
            "AI returned an invalid action."
        )

    return {
        "action":
            result.get("action"),

        "field":
            result.get("field"),

        "value":
            result.get("value"),

        "message":
            result.get("message")
            or "Command processed."
    }