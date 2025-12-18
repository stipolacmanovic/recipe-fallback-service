import json
import ast
import logging
from typing import Optional
from openai import AsyncOpenAI
from openai import APIError
from core.config import OPENAI_API_KEY, OPENAI_MODEL
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile

logger = logging.getLogger(__name__)


class RecipeGenerationError(Exception):
    """Custom exception for recipe generation errors with detailed message"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class RecipeGenerator:    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
        
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL


    async def generate_recipe(self, query: str) -> Optional[RecipeResponse]:

        prompt = f"""You are a professional bartender creating cocktail recipes in the Cocktail Club style.

Generate a complete, detailed cocktail recipe for: "{query}"

The recipe must be formatted as a JSON object with the following structure:
{{
    "title": "String - Cocktail name in UPPERCASE format (e.g., MARGARITA, WHISKEY SOUR)",
    "history": "String - Short history/origin starting with 'The [cocktail name]'s history...' (2-4 sentences, factual and general, include dates/places/people when known)",
    "technique": "String - Preparation technique (e.g., Shaken, Stirred, Built, Muddled)",
    "glass_type": "String - Recommended glass type (e.g., Coupe, Rocks Glass, Coupe or Rocks Glass, Highball)",
    "ingredients": [
        "Array of objects, each with:",
        "  - name: String - Ingredient name formatted as '[amount] oz ([amount] ml) [Ingredient Name]' or preparation note (e.g., 'Salt for rim', 'Egg White')",
        "  - oz: Number - Amount in ounces (use 0.0 for non-liquid ingredients)",
        "  - ml: Number - Amount in milliliters (use 0.0 for non-liquid ingredients)"
    ],
    "tasting_profile": {{
        "alcohol": "Integer 0-5 - Alcohol intensity (0=non-alcoholic, 5=very strong)",
        "bitter": "Integer 0-5 - Bitter intensity (0=none, 5=very intense)",
        "sour": "Integer 0-5 - Sour intensity (0=none, 5=very intense)",
        "sweet": "Integer 0-5 - Sweet intensity (0=none, 5=very intense)"
    }},
    "method": [
        "Array of strings - Step-by-step instructions (5-7 steps)",
        "Each step should start with action verb + colon (e.g., 'Prepare:', 'Ice:', 'Add ingredients:', 'Shake:', 'Strain:', 'Garnish and serve:')",
        "Include specific details: times, temperatures, techniques"
    ],
    "tip": "String - Practical bartender's tip with actionable advice, can include variations with specific measurements (1-3 sentences)"
}}


CRITICAL REQUIREMENTS - Follow the Cocktail Club style exactly:

1. **Title**: Use UPPERCASE format (e.g., "MARGARITA", "WHISKEY SOUR")

2. **History**: 
   - Always start with "The [cocktail name]'s history..." or similar opening
   - Write 2-4 sentences that are factual and general
   - Include specific historical details (dates, places, people) when known
   - If origin is disputed, mention the most popular theories
   - Use narrative, engaging style

3. **Technique**: 
   - Use single word or short phrase: "Shaken", "Stirred", "Built", "Muddled", "Shaken (dry shake then wet shake)"
   - Common techniques: Shaken, Stirred, Built, Muddled

4. **Glass Type**: 
   - Specify the recommended glass: "Coupe", "Rocks Glass", "Coupe or Rocks Glass", "Highball", "Martini Glass", etc.
   - Can list alternatives if multiple are appropriate

5. **Ingredients**:
   - Format ingredient names as: "[amount] oz ([amount] ml) [Ingredient Name]"
   - Include preparation notes when relevant (e.g., "Salt for rim", "Egg White", "Sugar for rim (optional)")
   - Provide accurate oz and ml values (use standard conversions: 1 oz = 29.5735 ml, round to whole numbers or one decimal place)
   - For non-liquid ingredients (salt, garnishes, bitters), use oz: 0.0, ml: 0.0
   - List ingredients in order of use or by volume (largest first)

6. **Tasting Profile**: 
   - Use integers 0-5 for each dimension
   - Be accurate based on the cocktail's actual characteristics
   - Alcohol: 0 (non-alcoholic) to 5 (very strong)
   - Bitter, Sour, Sweet: 0 (none) to 5 (very intense)

7. **Method**:
   - Each step should start with an action verb followed by a colon (Prepare:, Ice:, Add ingredients:, Shake:, Strain:, Garnish and serve:, etc.)
   - Include specific details: times (e.g., "10-15 seconds"), temperatures ("chilled"), techniques ("double-strain")
   - Be detailed and instructional, like: "Prepare: Rim a chilled coupe or rocks glass with salt. To do this, run a lime wedge around the rim and dip it onto a plate of coarse salt."
   - Include 5-7 detailed steps
   - Each step should be a complete sentence with clear instructions

8. **Tip**:
   - Provide practical, actionable advice
   - Can include variations or modifications with specific measurements
   - Should be helpful for bartenders making the drink
   - Can be 1-3 sentences with specific measurements or techniques
   - Example style: "For a spicy kick, muddle a few slices of jalapeño in the shaker before adding the other ingredients. For a smoother, richer texture, add 0.5 oz (15 ml) of agave nectar and reduce the triple sec to 0.5 oz (15 ml)."

9. **Style**: Write in a professional, engaging tone suitable for hospitality staff. Be specific and detailed. Match the format and detail level of classic cocktail recipes.

Return ONLY valid JSON. Do not include any markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional bartender creating detailed cocktail recipes in the Cocktail Club style. Your recipes should be professional, engaging, and suitable for hospitality staff. Always return valid JSON only, matching the exact format specified."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_completion_tokens=2000,
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

        except APIError as e:
            # Extract the actual error message from OpenAI API error
            error_message = str(e)
            
            # Try to extract message from exception body if available (OpenAI SDK v1.x)
            if hasattr(e, 'body') and e.body:
                try:
                    if isinstance(e.body, dict) and 'error' in e.body:
                        if 'message' in e.body['error']:
                            error_message = e.body['error']['message']
                except (ValueError, TypeError, AttributeError):
                    pass
            
            # Try to parse error message from string format: "Error code: XXX - {'error': {'message': '...'}}"
            if "Error code:" in error_message and "'error'" in error_message:
                try:
                    # Extract the dict part after "Error code: XXX - "
                    dict_start = error_message.find("{")
                    if dict_start != -1:
                        dict_str = error_message[dict_start:]
                        error_dict = ast.literal_eval(dict_str)
                        if 'error' in error_dict and 'message' in error_dict['error']:
                            error_message = error_dict['error']['message']
                except (ValueError, SyntaxError):
                    pass
            
            if "429" in error_message or "insufficient_quota" in error_message or "quota" in error_message.lower():
                logger.error(
                    f"OpenAI API quota exceeded or billing issue. "
                    f"Please check your OpenAI account billing and usage limits. "
                    f"Error: {error_message}"
                )
            else:
                logger.error(f"Error generating recipe: {error_message}")
            raise RecipeGenerationError(error_message, e)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating recipe: {error_msg}")
            raise RecipeGenerationError(error_msg, e)


_recipe_generator: Optional[RecipeGenerator] = None


def get_recipe_generator() -> RecipeGenerator:
    global _recipe_generator
    if _recipe_generator is None:
        _recipe_generator = RecipeGenerator()
    return _recipe_generator

