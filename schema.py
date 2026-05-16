from pydantic import BaseModel, Field

class CustomerTicketResolution(BaseModel):
    ticket_id: str = Field(...,description="The unique ticket ID generated for the customer's query using the generate_ticket_id tool.")
    resolution_steps: str = Field(...,description="The technical resolution steps retrieved using the get_resolution_guide tool.")
    loyalty_status: str = Field(...,description="The customer's loyalty status and perks determined using the check_loyalty_perks tool.")
    recent_orders: str = Field(...,description="The customer's recent order history retrieved using the fetch_order_history tool.")
    warranty_status: str = Field(...,description="The device's warranty status verified using the verify_warranty_status tool.")
    knowledge_base_answer: str = Field(...,description="Any additional information retrieved from searching the knowledge base (PDF documents) or custom inserted data. If none, say 'No additional context needed.'")
