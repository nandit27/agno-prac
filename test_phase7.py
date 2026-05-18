import asyncio
from agent import billing_support
from agno.utils.log import set_log_level_to_info
set_log_level_to_info()

async def main():
    print("\n--- PHASE 7: Guardrails & HITL & Hooks Test ---\n")
    await billing_support.arun("My credit card is 4000 1234 5678. I need a $15000 refund for my order #888")

if __name__ == "__main__":
    asyncio.run(main())
