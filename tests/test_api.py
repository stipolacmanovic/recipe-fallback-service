import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from services.recipe_service import search_recipe_by_query, create_recipe
from schemas.recipe import RecipeResponse, Ingredient, TastingProfile
from db.base import Base, get_db
from main import app
from httpx import AsyncClient, ASGITransport


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def sample_recipe_data():
    return {
        "title": "MARGARITA",
        "search_query": "margarita",
        "history": "The Margarita's history is famously murky.",
        "technique": "Shaken",
        "glass_type": "Coupe or Rocks Glass",
        "ingredients": [
            {"name": "1.75 oz (60 ml) Tequila", "oz": 1.75, "ml": 60},
            {"name": "0.75 oz (25 ml) Lime Juice", "oz": 0.75, "ml": 25},
            {"name": "0.75 oz (25 ml) Triple Sec", "oz": 0.75, "ml": 25},
        ],
        "tasting_profile": {
            "alcohol": 4,
            "bitter": 1,
            "sour": 4,
            "sweet": 2
        },
        "method": [
            "Prepare: Rim a chilled coupe or rocks glass with salt.",
            "Ice: Fill your cocktail shaker with cubed ice.",
            "Add ingredients: Pour in the tequila, lime juice, and triple sec.",
            "Shake: Close the shaker and shake hard for 10-15 seconds.",
            "Strain: Double-strain the cocktail into your prepared glass.",
            "Garnish and serve: Garnish with a lime wheel."
        ],
        "tip": "For a spicy kick, muddle a few slices of jalapeño."
    }


@pytest.fixture(scope="function")
async def test_client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_db_hit_recipe_found(db_session, sample_recipe_data):
    recipe = await create_recipe(db_session, sample_recipe_data)
    search_query = sample_recipe_data["search_query"]
    
    with patch('api.routes.get_recipe_generator') as mock_get_generator:
        mock_generator = AsyncMock()
        mock_generator.generate_recipe = AsyncMock()
        mock_get_generator.return_value = mock_generator
        
        found_recipe = await search_recipe_by_query(db_session, search_query)
        
        assert found_recipe is not None
        assert found_recipe.title == sample_recipe_data["title"]
        assert found_recipe.id == recipe.id
        
        mock_generator.generate_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_db_miss_recipe_not_found(db_session):
    test_queries = ["nonexistent cocktail", "unknown drink", "random query"]
    
    for query in test_queries:
        found_recipe = await search_recipe_by_query(db_session, query)
        assert found_recipe is None, f"Query '{query}' should not be found in empty database"


@pytest.mark.asyncio
async def test_llm_fallback_triggered_on_db_miss(test_client, db_session):
    test_query = "new cocktail"
    mock_recipe = RecipeResponse(
        title="NEW COCKTAIL",
        history="A new cocktail recipe history.",
        technique="Shaken",
        glass_type="Coupe",
        ingredients=[
            Ingredient(name="2 oz (60 ml) Gin", oz=2.0, ml=60),
            Ingredient(name="1 oz (30 ml) Lime Juice", oz=1.0, ml=30)
        ],
        tasting_profile=TastingProfile(alcohol=3, bitter=1, sour=3, sweet=2),
        method=[
            "Step 1: Add gin and lime juice to shaker",
            "Step 2: Shake with ice",
            "Step 3: Strain into coupe glass"
        ],
        tip="Garnish with a lime wheel"
    )
    
    with patch('api.routes.get_recipe_generator') as mock_get_generator:
        mock_generator = AsyncMock()
        mock_generator.generate_recipe = AsyncMock(return_value=mock_recipe)
        mock_get_generator.return_value = mock_generator

        response = await test_client.get(f"/recipe?query={test_query}")
        
        mock_generator.generate_recipe.assert_called_once_with(test_query)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == mock_recipe.title
        assert len(data["ingredients"]) == len(mock_recipe.ingredients)
        assert "ingredients" in data
        assert "method" in data


@pytest.mark.asyncio
async def test_query_validator_cocktail_query():
    from services.query_validator import validate_cocktail_wine_query
    
    valid_queries = [
        "margarita",
        "whiskey sour",
        "sidecar",
        "gin",
        "vodka",
        "martini"
    ]
    
    for query in valid_queries:
        is_valid, error = validate_cocktail_wine_query(query)
        assert is_valid is True, f"Query '{query}' should be valid: {error}"


@pytest.mark.asyncio
async def test_query_validator_wine_query():
    from services.query_validator import validate_cocktail_wine_query
    
    valid_queries = [
        "pinot noir",
        "chardonnay",
        "bordeaux",
        "wine",
        "champagne",
        "merlot"
    ]
    
    for query in valid_queries:
        is_valid, error = validate_cocktail_wine_query(query)
        assert is_valid is True, f"Query '{query}' should be valid: {error}"


@pytest.mark.asyncio
async def test_query_validator_rejects_food_queries():
    from services.query_validator import validate_cocktail_wine_query
    
    invalid_queries = [
        "chicken recipe",
        "pasta",
        "how to cook pizza",
        "baking cake",
        "soup",
        "salad"
    ]
    
    for query in invalid_queries:
        is_valid, error = validate_cocktail_wine_query(query)
        assert is_valid is False, f"Query '{query}' should be invalid"
        assert "cocktail" in error.lower() or "wine" in error.lower(), f"Error should mention cocktail/wine for '{query}'"


@pytest.mark.asyncio
async def test_query_validator_empty_query():
    from services.query_validator import validate_cocktail_wine_query
    
    empty_queries = ["", "   ", "\t", "\n"]
    
    for query in empty_queries:
        is_valid, error = validate_cocktail_wine_query(query)
        assert is_valid is False, f"Empty query '{repr(query)}' should be invalid"
        if query.strip() == "":
            assert "empty" in error.lower()

