from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cocktail Club Hospitality – AI Recipe Fallback Service (v1)",
    description="API that accepts a user query and returns a structured JSON recipe response.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to AI Recipe Fallback Service"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

