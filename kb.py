import os
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector

# DB connection using psycopg2 as specified in pgvector extension docs
DB_URL = "postgresql+psycopg://user:password@localhost:5432/agno_memory"

vector_db = PgVector(table_name="agent_knowledge", db_url=DB_URL)
knowledge_base = Knowledge(vector_db=vector_db)

async def load_initial_pdfs_async():
    """Loads the 3 PDFs from the pdfs directory into pgvector."""
    # check if table exists or vectors populated is up to user, we'll insert them here
    print("Loading PDFs into Knowledge Base... (Async)")
    pdf_files = ["pdfs/pdf-1.pdf", "pdfs/pdf-2.pdf", "pdfs/pdf-3.pdf"]
    for pdf in pdf_files:
        if os.path.exists(pdf):
            print(f"Ingesting {pdf}...")
            # Use async insert
            await knowledge_base.ainsert(path=pdf)
    print("Knowledge base ready!")
