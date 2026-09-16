from app.complaint_graph import complaint_graph


complaint_text = """
Apollo Pharmacy reported a complaint on 11 September 2026
regarding Amoxicillin Capsules 500 mg, batch AMX240602.

The customer received a sealed bottle containing 12 discolored
capsules. The product was manufactured on 1 March 2026 and
expires on 28 February 2028.

The customer requested an investigation into the product quality.
"""


initial_state = {
    "complaint_text": complaint_text
}


result = complaint_graph.invoke(initial_state)


print("\nLangGraph Result:")
print(result)