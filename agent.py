import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb

from schema import CustomerTicketResolution
from tools import (
    generate_ticket_id,
    get_resolution_guide,
    check_loyalty_perks,
    fetch_order_history,
    verify_warranty_status,
    insert_data_into_knowledge_base
)
from kb import knowledge_base

from dotenv import load_dotenv

load_dotenv()

DB_URL = "postgresql://user:password@localhost:5432/agno_memory"

def get_support_agent() -> Agent:
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[
            generate_ticket_id, 
            get_resolution_guide, 
            check_loyalty_perks, 
            fetch_order_history, 
            verify_warranty_status,
            insert_data_into_knowledge_base
        ],
        knowledge=knowledge_base,
        search_knowledge=True,
        # --- MEMORY CONFIGURATION ---
        db=PostgresDb(
            session_table="customer_support_sessions",
            memory_table="customer_support_memory",
            db_url=DB_URL
        ),
        update_memory_on_run=True,
        add_history_to_context=True,
        session_id="session-user-1234",
        # ----------------------------
        output_schema=CustomerTicketResolution,
        instructions=[
            "You are an advanced Customer Support Coordinator.",
            "Whenever a user submits an issue, you MUST use your tools IN PARALLEL to gather all required information:",
            "1. Generate a ticket ID using `generate_ticket_id`.",
            "2. Retrieve resolution steps using `get_resolution_guide`.",
            "3. Check the customer's loyalty perks using `check_loyalty_perks`.",
            "4. Fetch order history using `fetch_order_history`.",
            "5. Verify the device warranty status using `verify_warranty_status`.",
            "Call all the tools concurrently. Once you have all pieces of information, formulate your output to perfectly match the Pydantic schema.",
            "You can also search your knowledge base (which contains PDF info) to answer questions, or use `insert_data_into_knowledge_base` to store new rules/info."
        ],
        structured_outputs=True
    )

def get_memory_agent() -> Agent:
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        db=PostgresDb(
            session_table="customer_support_sessions",
            memory_table="customer_support_memory", 
            db_url=DB_URL
        ),
        knowledge=knowledge_base,
        search_knowledge=True,
        add_history_to_context=True,
        session_id="session-user-1234",
    )