from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Ingredient(BaseModel):
    name: str = Field(..., description="Ingredient name", min_length=1)
    oz: float = Field(..., ge=0, description="Amount in ounces")
    ml: float = Field(..., ge=0, description="Amount in milliliters")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ingredient name cannot be empty")
        return v.strip()


class TastingProfile(BaseModel):
    alcohol: int = Field(..., ge=0, le=5, description="Alcohol intensity (0-5)")
    bitter: int = Field(..., ge=0, le=5, description="Bitter intensity (0-5)")
    sour: int = Field(..., ge=0, le=5, description="Sour intensity (0-5)")
    sweet: int = Field(..., ge=0, le=5, description="Sweet intensity (0-5)")


class RecipeResponse(BaseModel):
    title: str = Field(..., description="Cocktail title", min_length=1)
    history: Optional[str] = Field(None, description="Short history/origin (2-4 sentences)")
    technique: Optional[str] = Field(None, description="Preparation technique")
    glass_type: Optional[str] = Field(None, description="Recommended glass type")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients with measurements", min_length=1)
    tasting_profile: Optional[TastingProfile] = Field(None, description="Tasting profile on 0-5 scale")
    method: List[str] = Field(..., description="Step-by-step method", min_length=1)
    tip: Optional[str] = Field(None, description="Bartender's tip")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v: List[Ingredient]) -> List[Ingredient]:
        if not v or len(v) == 0:
            raise ValueError("At least one ingredient is required")
        return v
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one method step is required")
        validated_steps = []
        for step in v:
            if not step or not step.strip():
                raise ValueError("Method steps cannot be empty")
            validated_steps.append(step.strip())
        return validated_steps
    
    @field_validator('history', 'technique', 'glass_type', 'tip')
    @classmethod
    def validate_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            return None
        return v.strip() if v else None
