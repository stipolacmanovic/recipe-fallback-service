from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from db.base import get_db
from services.recipe_service import (
    create_recipe,
    search_recipe_by_query,
    recipe_to_response,
)
from services.llm_recipe_generator import get_recipe_generator, RecipeGenerationError
from schemas.recipe import RecipeResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/recipe", tags=["recipe"])


@router.get("", response_model=RecipeResponse)
async def get_recipe(
    query: str = Query(..., min_length=1, description="Cocktail name or query"),
    db: AsyncSession = Depends(get_db)
):
    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required"
        )

    try:
        recipe = await search_recipe_by_query(db, query)
        if recipe:
            logger.info(f"Found recipe in database: {recipe.title}")
            return await recipe_to_response(recipe)

        try:
            logger.info(f"Generating recipe for query: {query}")
            recipe_response = await get_recipe_generator().generate_recipe(query)
            
            try:
                recipe_data = {
                    "title": recipe_response.title,
                    "search_query": query.strip(),  # Store original query for exact matching
                    "history": recipe_response.history,
                    "technique": recipe_response.technique,
                    "glass_type": recipe_response.glass_type,
                    "ingredients": [
                        {"name": ing.name, "oz": ing.oz, "ml": ing.ml}
                        for ing in recipe_response.ingredients
                    ],
                    "tasting_profile": (
                        {
                            "alcohol": recipe_response.tasting_profile.alcohol,
                            "bitter": recipe_response.tasting_profile.bitter,
                            "sour": recipe_response.tasting_profile.sour,
                            "sweet": recipe_response.tasting_profile.sweet
                        } if recipe_response.tasting_profile else None
                    ),
                    "method": recipe_response.method,
                    "tip": recipe_response.tip,
                }
                logger.info(f"Saving Generated Recipe in database: {recipe_data['title']}")
                await create_recipe(db, recipe_data)
            except Exception as e:
                logger.error(f"Error creating recipe: {e}")
            
            return recipe_response

        except ValueError as e:
            error_msg = str(e)
            if "OPENAI_API_KEY" in error_msg or "OpenAI API key" in error_msg:
                logger.error(f"OpenAI API key not configured: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable."
                )
            raise
        except RecipeGenerationError as e:
            logger.error(f"Error generating recipe: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating recipe: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg if error_msg else "Query must be related to cocktails"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting recipe for query '{query}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the recipe"
        )        
    
