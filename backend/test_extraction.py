from app.ai_service import extract_complaint


complaint_text = """
Apollo Pharmacy reported a customer complaint on 11 September 2026.

The complaint concerns Amoxicillin Capsules 500 mg, batch number AMX240602.
The customer received a sealed bottle containing 12 discolored capsules.

The product was manufactured on 1 March 2026 and expires on 28 February 2028.

The complaint type is product discoloration. The customer is concerned
about the quality of the medicine and requested investigation.
"""


result = extract_complaint(complaint_text)

print("Extracted Complaint:")
print(result)