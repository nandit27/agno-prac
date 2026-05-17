import time
import asyncio
import uuid
from kb import knowledge_base

async def generate_ticket_id(customer_name: str, issue_type: str) -> str:
    """Generates a unique tracking ticket ID."""
    print(f"[{time.strftime('%X')}] 🟡 Start generate_ticket_id")
    await asyncio.sleep(1) # Simulate network delay
    real_uuid = str(uuid.uuid4()).split("-")[0]
    
    clean_name = customer_name.replace(" ", "").upper()[:4]
    print(f"[{time.strftime('%X')}] 🟢 Finish generate_ticket_id")
    return f"TKT-{clean_name}-{issue_type.upper()}-{real_uuid}"

async def get_resolution_guide(issue_type: str) -> str:
    """Looks up the official corporate resolution steps."""
    print(f"[{time.strftime('%X')}] 🟡 Start get_resolution_guide")
    await asyncio.sleep(2) # Simulate network delay
        
    knowledge_base_dict = {
        "login": "1. Send password reset link. 2. Verify email. 3. Unlock account.",
        "refund": "1. Verify order. 2. Process via Stripe. 3. Send email confirmation.",
        "damage": "1. Request photos. 2. Issue return label. 3. Send replacement."
    }
    print(f"[{time.strftime('%X')}] 🟢 Finish get_resolution_guide")
    return knowledge_base_dict.get(issue_type.lower(), "Standard resolution: escalate to human agent.")

async def check_loyalty_perks(customer_email: str) -> str:
    """Checks if the customer has VIP perks."""
    print(f"[{time.strftime('%X')}] 🟡 Start check_loyalty_perks")
    await asyncio.sleep(2)
    print(f"[{time.strftime('%X')}] 🟢 Finish check_loyalty_perks")
    if "vip" in customer_email.lower():
        return "Customer is VIP. Eligible for expedited shipping and 15% discount."
    return "Customer is Standard. Offer standard support."

async def fetch_order_history(customer_email: str) -> str:
    """Retrieves recent orders placed by the customer using their email."""
    print(f"[{time.strftime('%X')}] 🟡 Start fetch_order_history")
    await asyncio.sleep(2)
    print(f"[{time.strftime('%X')}] 🟢 Finish fetch_order_history")
    if "vip" in customer_email.lower():
        return "Order #98765 (Delivered 2 days ago), Order #98711 (Delivered 1 month ago)"
    return "Order #12345 (Pending)"

async def verify_warranty_status(order_id: str) -> str:
    """Verifies if the order is under warranty."""
    print(f"[{time.strftime('%X')}] 🟡 Start verify_warranty_status")
    await asyncio.sleep(2)
    print(f"[{time.strftime('%X')}] 🟢 Finish verify_warranty_status")
    if "987" in order_id:
        return "Warranty ACTIVE - Covers all labor and replacement parts until 2028."
    return "Warranty EXPIRED - Out of coverage period."

async def insert_data_into_knowledge_base(text_data: str, data_name: str = "custom_data") -> str:
    """Inserts custom text data into the Postgres vector knowledge base."""
    print(f"[{time.strftime('%X')}] 🟡 Start insert_data_into_knowledge_base")
    await asyncio.sleep(1)
    await knowledge_base.ainsert(text_content=text_data, name=data_name)
    print(f"[{time.strftime('%X')}] 🟢 Finish insert_data_into_knowledge_base")
    return f"Success: the data under name '{data_name}' was inserted into the knowledge base."
