from pydantic import BaseModel, Field
from typing import List, Optional


class Ingredient(BaseModel):
    name: str = Field(..., description="Ingredient name")
    oz: float = Field(..., ge=0, description="Amount in ounces")
    ml: float = Field(..., ge=0, description="Amount in milliliters")


class TastingProfile(BaseModel):
    alcohol: int = Field(..., ge=0, le=5, description="Alcohol intensity (0-5)")
    bitter: int = Field(..., ge=0, le=5, description="Bitter intensity (0-5)")
    sour: int = Field(..., ge=0, le=5, description="Sour intensity (0-5)")
    sweet: int = Field(..., ge=0, le=5, description="Sweet intensity (0-5)")


class RecipeResponse(BaseModel):
    title: str = Field(..., description="Cocktail title")
    history: Optional[str] = Field(None, description="Short history/origin (2-4 sentences)")
    technique: Optional[str] = Field(None, description="Preparation technique")
    glass_type: Optional[str] = Field(None, description="Recommended glass type")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients with measurements")
    tasting_profile: Optional[TastingProfile] = Field(None, description="Tasting profile on 0-5 scale")
    method: List[str] = Field(..., description="Step-by-step method")
    tip: Optional[str] = Field(None, description="Bartender's tip")
