from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from typing import Optional
import logging
from models.recipe import Recipe
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile
import hashlib

logger = logging.getLogger(__name__)


def generate_recipe_id(query: str) -> str:
    normalized = query.lower().strip()
    hash_obj = hashlib.md5(normalized.encode())
    return f"recipe_{hash_obj.hexdigest()[:12]}"


async def search_recipe_by_query(
    db: AsyncSession,
    query: str
) -> Optional[Recipe]:
    query_lower = query.lower().strip()
    
    result = await db.execute(
        select(Recipe).where(
            sql_func.lower(Recipe.title) == query_lower
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

