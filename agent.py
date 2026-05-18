import os
from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb

from schema import CustomerTicketResolution
from tools import (
    generate_ticket_id,
    get_resolution_guide,
    check_loyalty_perks,
    fetch_order_history,
    verify_warranty_status,
    insert_data_into_knowledge_base,
    issue_refund,
    issue_large_refund
)
from kb import knowledge_base

from dotenv import load_dotenv

load_dotenv()

DB_URL = "postgresql://user:password@localhost:5432/agno_memory"
MODEL = OpenAIChat(id="gpt-4o-mini")

# team 1 - coordinate mode
ticket_agent = Agent(
    name="Ticket Agent", 
    role="Generate ticket identifiers for tracking", 
    tools=[generate_ticket_id], 
    model=MODEL
)

resolution_agent = Agent(
    name="Resolution Agent", 
    role="Search knowledge base and resolution guides", 
    tools=[get_resolution_guide, insert_data_into_knowledge_base], 
    knowledge=knowledge_base, 
    search_knowledge=True, 
    reasoning=True, 
    model=MODEL
)

account_agent = Agent(
    name="Account Agent", 
    role="Handle order history, warranty, and loyalty tracking", 
    tools=[fetch_order_history, verify_warranty_status, check_loyalty_perks], 
    model=MODEL
)

def _coordinate_members(session_state: dict = None):
    session_state = session_state or {}
    tier = session_state.get("customer_tier", "basic")
    if tier == "premium":
        members = [ticket_agent, resolution_agent, account_agent]
    else:
        members = [ticket_agent, resolution_agent]
    print(f"\\n[Factory] _coordinate_members executing... Tier: '{tier}' -> Members: {[m.name for m in members]}")
    return members

def get_coordinate_team() -> Team:
    return Team(
        name="Support Coordinate Team",
        mode=TeamMode.coordinate,
        members=_coordinate_members,
        cache_callables=False,
        reasoning=True,
        instructions=[
            "Coordinate among your members to handle open-ended customer support issues fully.",
            "Use your members to generate a ticket, retrieve resolution guides, and verify warranties and orders.",
            "CRITICAL: Do NOT output placeholder messages like 'I am delegating', 'Please wait', or 'I am gathering responses'.",
            "You must wait for the data from your members internally and output ONLY the final comprehensive response to the user."
        ],
        model=MODEL,
    )

# ==========================================
# Phase 7: Hooks & Guardrails Definitions
# ==========================================
def pii_guardrail(agent: Agent, **kwargs) -> None:
    """PRE-HOOK: Mask Credit Card information before LLM sees it."""
    run_request = kwargs.get("run_request", {})
    if hasattr(run_request, "messages"):
        for msg in run_request.messages:
            if isinstance(msg, dict) and "content" in msg and "4000" in msg.get("content", ""):
                print(">> [GUARDRAIL INTERCEPT] PII Masked <<")
                msg["content"] = msg["content"].replace("4000", "XXXX")
    elif isinstance(run_request, dict) and "messages" in run_request:
        for msg in run_request["messages"]:
            if isinstance(msg, dict) and "content" in msg and "4000" in msg.get("content", ""):
                print(">> [GUARDRAIL INTERCEPT] PII Masked <<")
                msg["content"] = msg["content"].replace("4000", "XXXX")
    
    # Also check the raw message passed in kwargs if available
    message = kwargs.get("message")
    if hasattr(message, "content") and message.content and "4000" in message.content:
         print(">> [GUARDRAIL INTERCEPT] PII Masked <<")
         message.content = message.content.replace("4000", "XXXX")

def audit_logger_hook(agent: Agent, **kwargs) -> None:
    """POST-HOOK: Write to database audit log in background."""
    print(f">> [AUDIT LOG] Transaction logged for agent: {agent.name} without slowing down user response. <<")

# team 2 - route mode
tech_support = Agent(
    name="Technical Support", 
    role="Hardware and software troubleshooting", 
    tools=[get_resolution_guide], 
    knowledge=knowledge_base, 
    search_knowledge=True, 
    reasoning=True, 
    instructions=["Always use the search_knowledge_base tool to look up technical documents, manuals, and troubleshooting steps. If a document number is provided, search for it."],
    model=MODEL
)

billing_support = Agent(
    name="Billing & Orders", 
    role="Check order history, loyalty perks, and process refunds strictly.", 
    tools=[fetch_order_history, check_loyalty_perks, issue_refund, issue_large_refund], 
    instructions="Process refunds strictly. Do not repeat tool calls after a successful refund. If the requested refund is > $500, you MUST use the `issue_large_refund` tool to ensure Admin Approval. If it is <= $500, use `issue_refund`.",
    reasoning=True, 
    model=MODEL,
    pre_hooks=[pii_guardrail],
    post_hooks=[audit_logger_hook],
)

warranty_support = Agent(
    name="Warranty Queries",
    role="Verify warranty status for serial numbers",
    tools=[verify_warranty_status], 
    reasoning=True, 
    model=MODEL
)

def _route_members(session_state: dict = None):
    session_state = session_state or {}
    tier = session_state.get("customer_tier", "basic")
    if tier == "premium":
        members = [tech_support, billing_support, warranty_support]
    else:
        members = [tech_support, billing_support]
    print(f"\\n[Factory] _route_members executing... Tier: '{tier}' -> Members: {[m.name for m in members]}")
    return members

def get_route_team() -> Team:
    return Team(
        name="Support Route Team",
        mode=TeamMode.route,
        members=_route_members,
        cache_callables=False,
        reasoning=True,
        instructions="Identify the primary intent of the user's issue and route it to the single appropriate agent (Technical Support, Billing & Orders, or Warranty Queries).",
        model=MODEL
    )

# team 3 - broadcast mode
sentiment_analyzer = Agent(
    name="Sentiment Analyzer", 
    role="Analyze the emotional tone and urgency of the customer", 
    reasoning=True, 
    model=MODEL
)

fraud_checker = Agent(
    name="Fraud Checker", 
    role="Check if the customer is eligible for loyalty perks", 
    tools=[check_loyalty_perks], 
    reasoning=True, 
    model=MODEL
)

kb_researcher = Agent(
    name="KB Researcher", 
    role="Check the knowledge base for any matching known issues", 
    tools=[get_resolution_guide], 
    knowledge=knowledge_base, 
    search_knowledge=True, 
    reasoning=True, 
    model=MODEL
)

def _broadcast_members(session_state: dict = None):
    session_state = session_state or {}
    tier = session_state.get("customer_tier", "basic")
    if tier == "premium":
        members = [sentiment_analyzer, fraud_checker, kb_researcher]
    else:
        members = [sentiment_analyzer, kb_researcher]
    print(f"\\n[Factory] _broadcast_members executing... Tier: '{tier}' -> Members: {[m.name for m in members]}")
    return members

def get_broadcast_team() -> Team:
    return Team(
        name="Support Broadcast Team",
        mode=TeamMode.broadcast,
        members=_broadcast_members,
        cache_callables=False,
        reasoning=True,
        instructions="Broadcast the user's query to all members. Synthesize their analysis (sentiment, fraud check, and KB research) into one comprehensive report.",
        model=MODEL
    )


# ==========================================
# Preservation of existing agents (memory)
# ==========================================
# Optionally, if still needed by main.py for backwards compatibility tests:
def get_memory_agent() -> Agent:
    return Agent(
        model=MODEL,
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