import asyncio
import json
from pydantic import BaseModel, Field
from typing import List, Optional, Iterator, Union, Dict, Any

from agno.workflow import Workflow
from agno.agent import Agent
from agno.models.groq import Groq

from agno.utils.log import logger
from dotenv import load_dotenv

load_dotenv()

# Import existing async tools 
from tools import (
    fetch_order_history,
    check_loyalty_perks,
    get_resolution_guide
)

# ---------------------------------------------------------
# Phase 5: Pydantic Typed Inputs and Outputs
# ---------------------------------------------------------
class SupportInput(BaseModel):
    customer_email: str = Field(..., description="Customer's email address")
    issue_type: str = Field(..., description="Category of the issue (e.g., login, refund, outage)")

class OrderDetail(BaseModel):
    order_id: str
    status: str

class SupportOutput(BaseModel):
    customer_email: str
    loyalty_status: str
    resolution_steps: str
    orders_checked: List[OrderDetail]
    final_report: str

class CustomerSupportWorkflow(Workflow):
    description: str = "A deterministic workflow for handling customer support tasks."

    # Agents used in the workflow
    reporter_agent: Agent = Agent(
        name="Reporter Agent",
        role="Compile the final customer report",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions="Summarize the loyalty status, resolution guide, and order history into a cohesive response to the customer."
    )

    escalation_agent: Agent = Agent(
        name="Escalation Risk Agent",
        role="Handle VIP or Red Flag customers gracefully",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions="Draft a highly apologetic and prioritized white-glove response for a VIP customer based on the gathered data."
    )

    def run(self, support_request: SupportInput) -> Iterator[str]:
        logger.info(f"Starting workflow for customer: {support_request.customer_email}")

        # ---------------------------------------------------------
        # Requirement 4: Early Stop Condition
        # ---------------------------------------------------------
        if support_request.issue_type.lower() == "outage":
            yield "SYSTEM ALERT: Global outage detected. Please abort standard troubleshooting. Our engineers are working on it."
            return

        # ---------------------------------------------------------
        # Requirement 1: Parallel Execution
        # ---------------------------------------------------------
        # We need to run these concurrently to save wall time
        logger.info("Running independent data fetchers in parallel...")
        
        async def fetch_all():
            loyalty_task = check_loyalty_perks(support_request.customer_email)
            resolution_task = get_resolution_guide(support_request.issue_type)
            orders_task = fetch_order_history(support_request.customer_email)
            return await asyncio.gather(loyalty_task, resolution_task, orders_task)

        loyalty_result, resolution_result, orders_result = asyncio.run(fetch_all())

        logger.info("Parallel data gathered successfully.")

        # ---------------------------------------------------------
        # Requirement 2: Loop / Wrapping execution
        # ---------------------------------------------------------
        # Let's pretend the `orders_result` gave us a string of multiple orders. We will loop to structure it.
        # In a real app the fetch_order_history would return structured data, but we'll parse it for the loop.
        parsed_orders: List[OrderDetail] = []
        if "Order #" in orders_result:
            # Simple string parsing to simulate looping over a portfolio
            order_strings = orders_result.split(", ")
            for ord_str in order_strings:
                if "#" in ord_str:
                    logger.info(f"Looping over order: {ord_str}")
                    # e.g., "Order #98765 (Delivered 2 days ago)"
                    parts = ord_str.replace("Order ", "").split(" (")
                    o_id = parts[0]
                    status = parts[1].replace(")", "") if len(parts) > 1 else "Unknown"
                    parsed_orders.append(OrderDetail(order_id=o_id, status=status))

        # ---------------------------------------------------------
        # Requirement 3: Explicitly pass typed Inputs/Outputs
        # ---------------------------------------------------------
        workflow_data = {
            "loyalty": loyalty_result,
            "resolution": resolution_result,
            "orders": [o.model_dump() for o in parsed_orders]
        }
        json_data = json.dumps(workflow_data, indent=2)

        # ---------------------------------------------------------
        # Requirement 1 & 4 (Condition Branch): Condition(any_red_flag, true=RiskAgent)
        # ---------------------------------------------------------
        # If the customer is VIP, we consider that our "routing condition" to the Escalation agent.
        is_vip = "VIP" in loyalty_result

        logger.info(f"Condition Check: is_vip={is_vip}. Routing to appropriate agent.")
        if is_vip:
            active_agent = self.escalation_agent
        else:
            active_agent = self.reporter_agent

        # ---------------------------------------------------------
        # Final Step: Reporter Output
        # ---------------------------------------------------------
        yield f"--- Preparing response using {active_agent.name} ---\n\n"
        
        final_content = ""
        for chunk in active_agent.run(json_data, stream=True):
            if hasattr(chunk, 'content') and chunk.content is not None:
                final_content += chunk.content
                yield chunk.content
            elif isinstance(chunk, str):
                final_content += chunk
                yield chunk
        
        # We can construct the final Typed Output but we just yield the text string for the terminal runner.
        return


if __name__ == "__main__":
    from agno.utils.log import set_log_level_to_info
    set_log_level_to_info()
    
    workflow = CustomerSupportWorkflow()
    
    print("\n\n>>> RUN 1: Standard Customer (login issue) <<<")
    # Should route to standard reporter
    req1 = SupportInput(customer_email="john@standard.com", issue_type="login")
    for output in workflow.run(req1):
        print(output, end="", flush=True)

    print("\n\n>>> RUN 2: VIP Customer Condition (refund issue) <<<")
    # Should use parallel loop + route to Escalation/Risk Agent for VIP
    req2 = SupportInput(customer_email="anna@vip.com", issue_type="refund")
    for output in workflow.run(req2):
        print(output, end="", flush=True)

    print("\n\n>>> RUN 3: Early Stop Trigger (outage issue) <<<")
    # Should bypass data fetching completely
    req3 = SupportInput(customer_email="mike@standard.com", issue_type="outage")
    for output in workflow.run(req3):
        print(output, end="", flush=True)
    print("\n")
