from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
from pydantic import BaseModel, Field
from typing import List, Optional

# Define Schema
class Recipe(BaseModel):
    recipe_name: str = Field(description="ឈ្មោះ Recipe")
    ingredients: List[str] = Field(description="ប្រការ Ingredient")
    prep_time_minutes: Optional[int] = Field(description="ពេលរៀបចំ (នាទី)")
    
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="ផ្ដល់ Recipe នំបុ័ង Banana",
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": Recipe.model_json_schema()
    },
)
# Parse Response
recipe = Recipe.model_validate_json(interaction.output_text)
print(recipe)