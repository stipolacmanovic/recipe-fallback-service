from fastapi import APIRouter, HTTPException, status, Query
import logging

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
    
    # Return test recipe
    return RecipeResponse(
        title="Old Fashioned",
        history="The Old Fashioned is one of the oldest known cocktails, dating back to the early 1800s. It was originally called a 'whiskey cocktail' and was made with whiskey, sugar, water, and bitters. The drink evolved over time, and by the 1880s, bartenders were adding various ingredients, leading purists to ask for their drink to be made 'the old-fashioned way'.",
        technique="Stirred",
        glass_type="Rocks glass",
        ingredients=[
            Ingredient(name="Bourbon whiskey", oz=2.0, ml=59.147),
            Ingredient(name="Angostura bitters", oz=0.083, ml=2.454),
            Ingredient(name="Simple syrup", oz=0.25, ml=7.393),
            Ingredient(name="Orange peel", oz=0.0, ml=0.0)
        ],
        tasting_profile=TastingProfile(
            alcohol=4,
            bitter=3,
            sour=1,
            sweet=2
        ),
        method=[
            "Place a sugar cube or simple syrup in a rocks glass",
            "Add Angostura bitters and muddle if using a sugar cube",
            "Add ice cubes to the glass",
            "Pour in the bourbon whiskey",
            "Stir gently for about 30 seconds to combine and chill",
            "Express an orange peel over the glass and drop it in as garnish"
        ],
        tip="Use a large ice cube or sphere to minimize dilution. The orange peel garnish adds essential oils that enhance the aroma and flavor of the drink.",
        image_prompt=None
    )
