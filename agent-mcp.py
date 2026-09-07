from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",

    input="""
    Check the weather in Phnom Penh using the MCP weather tool.
    Then explain the result.
    """,

    environment="remote",

    tools=[
        {
            "type": "mcp_server",
            "name": "weather",
            "url": "https://gemini-api-demos.uc.r.appspot.com/mcp"
        }
    ]
)

print("Environment:", interaction.environment_id)
print(interaction.output_text)