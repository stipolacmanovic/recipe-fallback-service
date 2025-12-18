from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from typing import Optional
import logging
from models.recipe import Recipe
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile

logger = logging.getLogger(__name__)


def normalize_for_search(text: str) -> str:
    if not text:
        return ""
    normalized = " ".join(text.lower().strip().split())
    return normalized


async def search_recipe_by_query(
    db: AsyncSession,
    query: str
) -> Optional[Recipe]:
    normalized_query = normalize_for_search(query)
    
    if not normalized_query:
        logger.warning(f"Empty query")
        return None
    
    result = await db.execute(
        select(Recipe).where(
            sql_func.lower(Recipe.search_query) == normalized_query
        )
    )
    recipe = result.scalar_one_or_none()
    
    if recipe:
        return recipe
    
    result = await db.execute(
        select(Recipe).where(
            sql_func.lower(Recipe.title) == normalized_query
        )
    )
    return result.scalar_one_or_none()


async def create_recipe(
    db: AsyncSession,
    recipe_data: dict
) -> Recipe:
    recipe = Recipe(**recipe_data)
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe


async def recipe_to_response(recipe: Recipe) -> RecipeResponse:
    ingredients = [
        Ingredient(**ing) for ing in recipe.ingredients
    ]
    
    tasting_profile = None
    if recipe.tasting_profile:
        tasting_profile = TastingProfile(**recipe.tasting_profile)
    
    return RecipeResponse(
        title=recipe.title,
        history=recipe.history,
        technique=recipe.technique,
        glass_type=recipe.glass_type,
        ingredients=ingredients,
        tasting_profile=tasting_profile,
        method=recipe.method,
        tip=recipe.tip
    )

