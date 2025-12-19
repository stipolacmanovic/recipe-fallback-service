import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Keywords related to cocktails
COCKTAIL_KEYWORDS = [
    # Cocktail types
    "cocktail", "drink", "beverage", "mixed drink",
    # Common cocktail names
    "margarita", "martini", "mojito", "old fashioned", "negroni", "daiquiri",
    "manhattan", "cosmopolitan", "moscow mule", "whiskey sour", "gin fizz",
    "bloody mary", "mimosa", "bellini", "aperol spritz", "sangria",
    "sidecar", "sazerac", "boulevardier", "aviation", "last word",
    # Techniques
    "shaken", "stirred", "built", "muddled", "blended",
    # Ingredients (alcohol)
    "gin", "vodka", "rum", "tequila", "whiskey", "whisky", "bourbon", "rye",
    "scotch", "brandy", "cognac", "liqueur", "vermouth", "bitters",
    # Glassware
    "coupe", "rocks glass", "highball", "martini glass", "champagne flute",
    # Terms (removed "recipe" - it's in negative keywords and handled by context)
    "how to make", "ingredients", "method"
]

# Keywords related to wine
WINE_KEYWORDS = [
    # Wine types
    "wine", "vintage", "wine bottle", "bottle of wine",
    # Wine categories
    "red wine", "white wine", "rosé", "rosé wine", "sparkling wine", "champagne",
    "prosecco", "cava", "port", "sherry", "dessert wine", "fortified wine",
    # Wine regions
    "bordeaux", "burgundy", "champagne", "tuscany", "rioja", "napa", "barolo",
    "chianti", "pinot noir", "cabernet", "merlot", "chardonnay", "sauvignon blanc",
    "riesling", "pinot grigio", "syrah", "shiraz", "malbec", "tempranillo",
    # Wine terms
    "vintage", "appellation", "terroir", "sommelier", "wine pairing",
    "wine tasting", "wine list", "wine cellar"
]

# Negative keywords (topics we want to reject)
NEGATIVE_KEYWORDS = [
    "food", "recipe", "cooking", "baking", "meal", "dish", "cuisine",
    "restaurant", "chef", "kitchen", "ingredient", "spice", "herb",
    "vegetable", "fruit", "meat", "chicken", "beef", "pork", "fish",
    "pasta", "pizza", "soup", "salad", "dessert", "cake", "bread"
]


def validate_cocktail_wine_query(query: str) -> Tuple[bool, str]:
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    query_lower = query.lower().strip()
    
    for negative_keyword in NEGATIVE_KEYWORDS:
        pattern = r'\b' + re.escape(negative_keyword) + r'\b'
        if re.search(pattern, query_lower):
            if not _is_cocktail_wine_context(query_lower, negative_keyword):
                logger.warning(f"Query rejected due to negative keyword: '{negative_keyword}' in '{query}'")
                return False, f"Query must be related to cocktails or wine only. Found unrelated topic: '{negative_keyword}'"
    
    cocktail_match = _check_keywords(query_lower, COCKTAIL_KEYWORDS)
    wine_match = _check_keywords(query_lower, WINE_KEYWORDS)
    
    if cocktail_match or wine_match:
        logger.info(f"Query validated as {'cocktail' if cocktail_match else 'wine'} related: '{query}'")
        return True, ""
    
    if _is_cocktail_name_pattern(query, query_lower):
        logger.info(f"Query validated as cocktail name pattern: '{query}'")
        return True, ""
    
    logger.warning(f"Query rejected - no cocktail/wine keywords found: '{query}'")
    return False, "Query must be related to cocktails or wine only. Please provide a cocktail name, wine type, or related query."


def _check_keywords(query: str, keywords: list) -> bool:
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query):
            return True
    return False


def _is_cocktail_name_pattern(query_original: str, query_lower: str) -> bool:
    cleaned_lower = re.sub(r'\b(the|a|an|how to make|recipe for|how to)\b', '', query_lower).strip()
    
    if not cleaned_lower:
        return False
    
    words = cleaned_lower.split()
    if not (1 <= len(words) <= 4):
        return False
    
    if any(len(word) < 2 for word in words):
        return False
    
    if any(word in cleaned_lower for word in ['what', 'where', 'when', 'why', 'how', '?']):
        return False
    
    cleaned_original = re.sub(r'\b(the|a|an|how to make|recipe for|how to)\b', '', query_original, flags=re.IGNORECASE).strip()
    
    if not cleaned_original:
        return False
    
    words_original = cleaned_original.split()
    
    if not words_original:
        return False
    
    all_uppercase = all(word.isupper() and len(word) >= 2 for word in words_original)
    
    all_title_case = all(
        len(word) >= 2 and word[0].isupper() and word[1:].islower() 
        for word in words_original
    )
    
    return all_uppercase or all_title_case


def _is_cocktail_wine_context(query: str, keyword: str) -> bool:
    if _check_keywords(query, COCKTAIL_KEYWORDS + WINE_KEYWORDS):
        return True
    
    exceptions = [
        ("recipe", ["cocktail", "drink", "wine"]),
        ("ingredient", ["cocktail", "drink", "wine", "gin", "vodka", "rum"]),
    ]
    
    for neg_keyword, context_keywords in exceptions:
        if keyword == neg_keyword:
            if any(ctx in query for ctx in context_keywords):
                return True
    
    return False

