import json
import asyncio
from openai import images
from pydantic import BaseModel, Field
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.media import Image
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Phase 6: Multimodal capabilities (Image to Structured Output)
# ---------------------------------------------------------------------------
# We are creating a visual debugging tool for the Customer Support Agent.
# Sometimes customers can't describe the error they are seeing, so they send a screenshot.
# The agent processes the screenshot and returns a structured diagnostic report.

class ErrorDiagnostic(BaseModel):
    is_error_present: bool = Field(..., description="True if an error message is visible in the screenshot.")
    error_code: str = Field(..., description="The specific error code or text shown. Return 'None' if none found.")
    affected_system: str = Field(..., description="The part of the system or app shown in the screenshot (e.g., 'Login Screen', 'Billing Dashboard').")
    recommended_troubleshooting: List[str] = Field(..., description="A simple list of 2-3 troubleshooting steps based strictly on the image content.")

# ---------------------------------------------------------------------------
# Create Multimodal Agent
# ---------------------------------------------------------------------------
# We use Groq for the text/json structuring processing. 
# Depending on Groq's multimodal support in your environment, typically you would 
# pass base64 or a URL. Here we pass a sample URL.

vision_debug_agent = Agent(
    name="Visual Debugger",
    role="Diagnose user errors based on application screenshots",
    # We switch to an OpenAI Vision-capable model as requested
    model=OpenAIChat(id="gpt-4o-mini"), 
    output_schema=ErrorDiagnostic,
    instructions="Analyze the provided screenshot. Identify any error messages, determine what part of the application is failing, and provide a structured troubleshooting report."
)

# ---------------------------------------------------------------------------
# Run Agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from agno.utils.log import set_log_level_to_info
    set_log_level_to_info()

    print("\n\n>>> Phase 6: Simulated Screenshot Debugging <<<\n")
    print("Customer: 'I am getting this weird error on the website. I have attached a screenshot.'")
    print("Agent Processing Image...\n")

    # We provide a sample image URL showing an error page (HTTP 404/500 style image)
    # Using a Wikimedia example image for demonstration purposes.
    response = vision_debug_agent.run(
        "Look at this screenshot the customer sent. What is the error and how do we guide them?",
        images=[
            Image(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Http_error_500.jpg/960px-Http_error_500.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail"
            )
        ]
    )

    # Because we specified output_schema=ErrorDiagnostic, the output is returned as structured data
    # (specifically, an ErrorDiagnostic Pydantic object if using full structured parsing, or a JSON chunk)
    
    diagnostic = response.content
    print("\n--- Multimodal Parsing Complete ---")
    if hasattr(diagnostic, 'model_dump_json'):
        print(diagnostic.model_dump_json(indent=2))
    else:
        # Fallback if standard str is returned by the framework parser
        print(diagnostic)

    print("\n")

# Testing images
# 1. https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Http_error_500.jpg/960px-Http_error_500.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail
# 2. https://upload.wikimedia.org/wikipedia/commons/5/5f/404_not_found.png?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original