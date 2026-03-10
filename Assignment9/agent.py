from agents import (
    Agent,
    WebSearchTool,
    FileSearchTool,
    ImageGenerationTool,
)
from config import VECTOR_STORE_ID, AGENT_NAME, AGENT_INSTRUCTIONS


def create_agent():
    return Agent(
        name=AGENT_NAME,
        instructions=AGENT_INSTRUCTIONS,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "high",
                    "output_format": "jpeg",
                    "partial_images": 1,
                }
            ),
        ],
    )
