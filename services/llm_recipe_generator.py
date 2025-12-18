import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, OPENAI_MODEL
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile

logger = logging.getLogger(__name__)


class RecipeGenerator:    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
        
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL


    async def generate_recipe(self, query: str) -> Optional[RecipeResponse]:

        prompt = f"""You are a cocktail expert creating a recipe in the Cocktail Club.

Generate a complete cocktail recipe for: "{query}"

The recipe must be formatted as a JSON object with the following structure:
{{
    "title": "Cocktail title",
    "history": "Short history/origin (2–4 sentences, factual and general)",
    "technique": "Preparation technique",
    "glass_type": "Recommended glass type",
    "ingredients": [
        {{"name": "Ingredient name", "oz": 2.0, "ml": 59.1}},
        {{"name": "Another ingredient", "oz": 1.0, "ml": 29.6}}
    ],
    "tasting_profile": {{
        "alcohol": 3,
        "bitter": 2,
        "sour": 2,
        "sweet": 2
    }},
    "method": [
        "Step 1 description",
        "Step 2 description",
        "Step 3 description"
    ],
    "tip": "One helpful bartender's tip for making this cocktail"
}}


Requirements:
- All measurements must be provided in both ounces (oz) and milliliters (ml)
- Tasting profile values must be integers between 0 and 5
- History should be 2-4 sentences, factual and general
- Method should be clear step-by-step instructions
- Tip should be practical and helpful
- If the query is not a real cocktail, create a reasonable interpretation

Return ONLY valid JSON. Do not include any markdown formatting or code blocks."""

        try:
            logger.info(f"Generating recipe via LLM for query: {query}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional bartender creating cocktail recipes in the Cocktail Club. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            
            recipe_data = json.loads(content)

            ingredients = [
                Ingredient(**ing) for ing in recipe_data.get("ingredients", [])
            ]
            
            tasting_profile_data = recipe_data.get("tasting_profile")
            tasting_profile = None
            if tasting_profile_data:
                tasting_profile = TastingProfile(**tasting_profile_data)
            
            recipe_response = RecipeResponse(
                title=recipe_data.get("title", query),
                history=recipe_data.get("history"),
                technique=recipe_data.get("technique"),
                glass_type=recipe_data.get("glass_type"),
                ingredients=ingredients,
                tasting_profile=tasting_profile,
                method=recipe_data.get("method", []),
                tip=recipe_data.get("tip")
            )
            
            return recipe_response

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                logger.error(
                    f"OpenAI API quota exceeded or billing issue. "
                    f"Please check your OpenAI account billing and usage limits. "
                    f"Error: {error_msg}"
                )
            else:
                logger.error(f"Error generating recipe: {error_msg}")
            raise Exception(e)


_recipe_generator: Optional[RecipeGenerator] = None


def get_recipe_generator() -> RecipeGenerator:
    global _recipe_generator
    if _recipe_generator is None:
        _recipe_generator = RecipeGenerator()
    return _recipe_generator

