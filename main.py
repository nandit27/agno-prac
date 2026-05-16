import asyncio
from agent import get_support_agent, get_memory_agent
from kb import load_initial_pdfs_async

async def main():
    # Ingest the local pdfs into PgVector
    await load_initial_pdfs_async()

    support_agent = get_support_agent()
    
    print("=== FIRST RUN: Structured Tool Calling ===")
    print("Enter your support query (e.g., your name, email, issue, and serial number).")
    test_query_1 = input("User: ")
    
    print("\nProcessing with ASYNC tools and streaming tokens in parallel...\n")
    await support_agent.aprint_response(test_query_1, stream=True)
    
    print("\n\n=== SECOND RUN: Testing the PostgreSQL Memory ===")
    print("We will create a BRAND NEW agent instance with no tools and no schemas, acting as a clean slate.")
    print("But we point it to the SAME session_id in Postgres, proving it can recall previous events.")
    print("Ask a follow-up question (e.g., 'What was my email?' or 'What serial number did I give you?').")
    
    memory_agent = get_memory_agent()
    
    test_query_2 = input("User: ")
    
    print("\nRecalling from PostgresDB...\n")
    await memory_agent.aprint_response(test_query_2, stream=True)

if __name__ == "__main__":
    asyncio.run(main())

# Testing Queries

# "Hi, I am Bob, email is vip@gmail.com, SN-X9090. What troubleshooting hints does document 361204-001 offer regarding Business Desktops hardware problems?"

# "My name is Alice. I have a problem with my login. Can you check the Warranty and Support Guide PDF and tell me the main terms mentioned in it?"

# "Hey, my email is test@xyz.com. Can you check David Robinson's Customer Loyalty Programs paper and summarize the best practices mentioned?"

# "My name is John, email valid@abc.com, SN-X123, issue is refund. First, please insert this new policy into the knowledge base: 'Starting from 2027, all devices must be shipped using FedEx exclusively'. After you insert it, tell me what the new shipping rules are for 2027 by searching the knowledge base."