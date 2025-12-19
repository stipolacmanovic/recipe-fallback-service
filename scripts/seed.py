import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.base import get_db, init_db
from services.recipe_service import create_recipe, search_recipe_by_query
from mock.mock_recipes import get_mock_recipes
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def seed_database():
    try:
        logger.info("Initializing database...")
        await init_db()
        
        async for db in get_db():
            mock_recipes = get_mock_recipes()
            
            created_count = 0
            skipped_count = 0
            
            for recipe_data in mock_recipes:
                query = recipe_data.get("search_query", recipe_data["title"])
                existing = await search_recipe_by_query(db, query)
                
                if existing:
                    logger.info(f"Skipping '{recipe_data['title']}' - already exists")
                    skipped_count += 1
                    continue
                
                try:
                    await create_recipe(db, recipe_data)
                    created_count += 1
                    logger.info(f"Created recipe: {recipe_data['title']}")
                except Exception as e:
                    logger.error(f"Error creating recipe '{recipe_data['title']}': {e}")
            
            logger.info(f"Seeding complete!")
            logger.info(f"  Created: {created_count} recipes")
            logger.info(f"  Skipped: {skipped_count} recipes")
            break
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        raise


async def main():    
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())

