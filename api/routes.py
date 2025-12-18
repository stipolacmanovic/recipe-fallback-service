from fastapi import APIRouter, HTTPException, status, Query
import logging

from services.llm_recipe_generator import get_recipe_generator
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/recipe", tags=["recipe"])


@router.get("", response_model=RecipeResponse)
async def get_recipe(
    query: str = Query(..., min_length=1, description="Cocktail name or query"),
):
    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required"
        )

    try:
        recipe = await get_recipe_generator().generate_recipe(query)
    except Exception as e:
        logger.error(f"Error generating recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be related to cocktails or wine"
        )
    return recipe
