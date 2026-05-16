import time
import httpx
from kb import knowledge_base

async def generate_ticket_id(customer_name: str, issue_type: str) -> str:
    """Generates a unique tracking ticket ID."""
    print(f"[{time.strftime('%X')}] 🟡 Start generate_ticket_id")
    async with httpx.AsyncClient() as client:
        # Fetching a real UUID from a public API
        resp = await client.get("https://httpbin.org/uuid")
        real_uuid = resp.json().get("uuid", "1234").split("-")[0]
    
    clean_name = customer_name.replace(" ", "").upper()[:4]
    print(f"[{time.strftime('%X')}] 🟢 Finish generate_ticket_id")
    return f"TKT-{clean_name}-{issue_type.upper()}-{real_uuid}"

async def get_resolution_guide(issue_type: str) -> str:
    """Looks up the official corporate resolution steps."""
    print(f"[{time.strftime('%X')}] 🟡 Start get_resolution_guide")
    async with httpx.AsyncClient() as client:
        # Real network I/O delay hitting an external endpoint
        await client.get("https://httpbin.org/delay/2")
        
    knowledge_base = {
        "login": "1. Send password reset link. 2. Verify email. 3. Unlock account.",
        "refund": "1. Verify order. 2. Process via Stripe. 3. Send email confirmation.",
        "damage": "1. Request photo evidence. 2. Dispatch replacement immediately."
    }
    print(f"[{time.strftime('%X')}] 🟢 Finish get_resolution_guide")
    return knowledge_base.get(issue_type.lower(), "Escalate to Human Agent: Guide not found.")

async def check_loyalty_perks(customer_email: str) -> str:
    """Checks the customer's tier based on their email."""
    print(f"[{time.strftime('%X')}] 🟡 Start check_loyalty_perks")
    async with httpx.AsyncClient() as client:
        await client.get("https://httpbin.org/delay/2")
    print(f"[{time.strftime('%X')}] 🟢 Finish check_loyalty_perks")
    if "vip" in customer_email.lower():
        return "Platinum Tier - Offer 20% discount on next purchase."
    return "Standard Tier - Offer standard support."

async def fetch_order_history(customer_email: str) -> str:
    """Retrieves recent orders placed by the customer using their email."""
    print(f"[{time.strftime('%X')}] 🟡 Start fetch_order_history")
    async with httpx.AsyncClient() as client:
        await client.get("https://httpbin.org/delay/2")
    print(f"[{time.strftime('%X')}] 🟢 Finish fetch_order_history")
    if "vip" in customer_email.lower():
        return "Order #98765 (Delivered 2 days ago), Order #98766 (Processing)"
    return "No recent orders found."

async def verify_warranty_status(product_serial: str) -> str:
    """Verifies if the customer's device is currently under warranty based on the serial number."""
    print(f"[{time.strftime('%X')}] 🟡 Start verify_warranty_status")
    async with httpx.AsyncClient() as client:
        await client.get("https://httpbin.org/delay/2")
    print(f"[{time.strftime('%X')}] 🟢 Finish verify_warranty_status")
    if product_serial.startswith("SN-X"):
        return "Warranty ACTIVE - Covers all labor and replacement parts until 2028."
    return "Warranty EXPIRED - Out of coverage period."

async def insert_data_into_knowledge_base(text_data: str, data_name: str = "custom_data") -> str:
    """Inserts custom text data into the Agent's knowledge base.
    
    Use this to add rules, policies, or facts given by the user into your permanent PGVector knowledge base.
    """
    print(f"[{time.strftime('%X')}] 🟡 Start insert_data_into_knowledge_base")
    await knowledge_base.ainsert(text_content=text_data, name=data_name)
    print(f"[{time.strftime('%X')}] 🟢 Finish insert_data_into_knowledge_base")
    return f"Success: the data under name '{data_name}' was inserted into the knowledge base."