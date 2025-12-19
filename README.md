# AI Recipe Fallback Service

A FastAPI-based REST API that provides cocktail and wine recipe generation. The service accepts queries and returns structured JSON recipe responses, using OpenAI's LLM as a fallback when recipes aren't found in the database.

## Setup with Docker

1. **Create a `.env` file** in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

2. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

The service will be available at http://localhost:8000

## Usage

### Get Recipe

**Endpoint:** `GET /recipe`

**Query Parameters:**
- `query` (required): Cocktail name or query (e.g., "margarita", "whiskey sour", "sidecar")

**Example Request:**
```bash
curl "http://localhost:8000/recipe?query=margarita"
```

**Example Response:**
```json
{
  "title": "MARGARITA",
  "history": "The Margarita's history is famously murky, with numerous claims to its invention...",
  "technique": "Shaken",
  "glass_type": "Coupe or Rocks Glass",
  "ingredients": [
    {
      "name": "1.75 oz (60 ml) Tequila",
      "oz": 1.75,
      "ml": 60
    },
    {
      "name": "0.75 oz (25 ml) Lime Juice",
      "oz": 0.75,
      "ml": 25
    },
    {
      "name": "0.75 oz (25 ml) Triple Sec",
      "oz": 0.75,
      "ml": 25
    }
  ],
  "tasting_profile": {
    "alcohol": 4,
    "bitter": 1,
    "sour": 4,
    "sweet": 2
  },
  "method": [
    "Prepare: Rim a chilled coupe or rocks glass with salt...",
    "Ice: Fill your cocktail shaker with cubed ice.",
    "Add ingredients: Pour in the tequila, lime juice, and triple sec.",
    "Shake: Close the shaker and shake hard for 10-15 seconds...",
    "Strain: Double-strain the cocktail into your prepared glass...",
    "Garnish and serve: Garnish with a lime wheel."
  ],
  "tip": "For a spicy kick, muddle a few slices of jalapeño..."
}
```

### Query Validation

The API validates queries to ensure they're related to cocktails or wine. Invalid queries (e.g., food recipes) will return a 400 error:

```json
{
  "detail": "Query must be related to cocktails or wine topics only"
}
```

### API Documentation

- **API docs**: http://localhost:8000/docs
- **UI**: http://localhost:8000 (simple HTML interface)
