import asyncio
from agent import (
    get_coordinate_team,
    get_route_team,
    get_broadcast_team
)
from kb import load_initial_pdfs_async

async def main():
    # Ingest the local pdfs into PgVector
    await load_initial_pdfs_async()

    coordinate_team = get_coordinate_team()
    route_team = get_route_team()
    broadcast_team = get_broadcast_team()
    
    print("\n" + "="*50)
    print("--- Testing Support Coordination (Coordinate Mode) ---")
    print("="*50)
    query1 = input("User (Team 1): ")
    if query1.strip():
        coordinate_team.session_state = {"customer_tier": "premium"}
        await coordinate_team.aprint_response(query1, stream=True)

    print("\n" + "="*50)
    print("--- Testing Intent Routing (Route Mode) ---")
    print("="*50)
    query2 = input("User (Team 2): ")
    if query2.strip():
        route_team.session_state = {"customer_tier": "premium"}
        await route_team.aprint_response(query2, stream=True)

    print("\n" + "="*50)
    print("--- Testing Parallel Analysis (Broadcast Mode) ---")
    print("="*50)
    query3 = input("User (Team 3): ")
    if query3.strip():
        broadcast_team.session_state = {"customer_tier": "premium"}
        await broadcast_team.aprint_response(query3, stream=True)

if __name__ == "__main__":
    asyncio.run(main())

# Test Queries
# 1: "Hi, I am Bob, email vip@gmail.com, SN-X9090. Need a ticket generated. Please check my order history and warranty status as well."
# 2: "What troubleshooting hints does document 361204-001 offer regarding Business Desktops hardware problems?"
# 3: "I am absolutely furious! My email is valid@abc.com, my new setup keeps randomly crashing! Check the knowledge base for crashing issues and tell me what my loyalty status gets me right now!"
