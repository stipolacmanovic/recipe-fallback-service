"""
Mock recipe dataset for testing and development.
Contains sample cocktail recipes in the format expected by the database.
"""
from typing import List, Dict

MOCK_RECIPES: List[Dict] = [
    {
        "title": "MARGARITA",
        "search_query": "margarita",
        "history": "The Margarita's history is famously murky, with numerous claims to its invention. The most popular story credits Carlos \"Danny\" Herrera, who supposedly created it in his Tijuana-area restaurant in 1938 for a showgirl named Marjorie King, who was allergic to all spirits except tequila.",
        "technique": "Shaken",
        "glass_type": "Coupe or Rocks Glass",
        "ingredients": [
            {"name": "1.75 oz (60 ml) Tequila", "oz": 1.75, "ml": 60},
            {"name": "0.75 oz (25 ml) Lime Juice", "oz": 0.75, "ml": 25},
            {"name": "0.75 oz (25 ml) Triple Sec", "oz": 0.75, "ml": 25},
            {"name": "Salt for rim", "oz": 0.0, "ml": 0.0}
        ],
        "tasting_profile": {
            "alcohol": 4,
            "bitter": 1,
            "sour": 4,
            "sweet": 2
        },
        "method": [
            "Prepare: Rim a chilled coupe or rocks glass with salt. To do this, run a lime wedge around the rim and dip it onto a plate of coarse salt.",
            "Ice: Fill your cocktail shaker with cubed ice.",
            "Add ingredients: Pour in the tequila, lime juice, and triple sec.",
            "Shake: Close the shaker and shake hard for 10-15 seconds until well-chilled.",
            "Strain: Double-strain the cocktail into your prepared glass. If serving on the rocks, fill the glass with fresh ice before straining.",
            "Garnish and serve: Garnish with a lime wheel."
        ],
        "tip": "For a spicy kick, muddle a few slices of jalapeño in the shaker before adding the other ingredients. For a smoother, richer texture, add 0.5 oz (15 ml) of agave nectar and reduce the triple sec to 0.5 oz (15 ml)."
    },
    {
        "title": "WHISKEY (WHISKY) SOUR",
        "search_query": "whiskey sour",
        "history": "The first printed recipe for a Whiskey Sour appeared in the 1862 book \"The Bon Vivant's Companion\" by Jerry Thomas. Sailors in the British Navy had been drinking something similar for centuries to combat scurvy, but Thomas codified the recipe for the masses.",
        "technique": "Shaken",
        "glass_type": "Rocks Glass",
        "ingredients": [
            {"name": "2 oz (60 ml) Bourbon or Rye Whiskey", "oz": 2.0, "ml": 60},
            {"name": "0.75 oz (25 ml) Fresh Lemon Juice", "oz": 0.75, "ml": 25},
            {"name": "0.75 oz (25 ml) Simple Syrup", "oz": 0.75, "ml": 25},
            {"name": "0.5 oz (15 ml) Egg White (optional)", "oz": 0.5, "ml": 15},
            {"name": "3 dashes Angostura Bitters", "oz": 0.0, "ml": 0.0}
        ],
        "tasting_profile": {
            "alcohol": 3,
            "bitter": 1,
            "sour": 4,
            "sweet": 3
        },
        "method": [
            "Prepare: If using egg white, separate it into your shaker.",
            "Add ingredients: Add the whiskey, lemon juice, and simple syrup to the shaker.",
            "Dry Shake: Close the shaker and shake hard without ice for 15 seconds to emulsify the egg white.",
            "Wet Shake: Add cubed ice to the shaker and shake again for 10-15 seconds until well-chilled.",
            "Strain: Strain into a chilled rocks glass filled with fresh ice.",
            "Garnish and serve: Garnish with a few dashes of Angostura bitters on top of the foam and a lemon wedge or cherry."
        ],
        "tip": "Always dry shake (shake without ice) first when using egg white to create a richer, more stable foam. Then, add ice and shake again (wet shake) to chill and dilute."
    },
    {
        "title": "SIDECAR",
        "search_query": "sidecar",
        "history": "The Sidecar was likely invented around the end of World War I in either London or Paris. The Ritz Hotel in Paris claims to have created it. The name is said to come from an American army captain who was driven to and from the bar in a motorcycle sidecar.",
        "technique": "Shaken",
        "glass_type": "Coupe",
        "ingredients": [
            {"name": "1.5 oz (40 ml) Cognac or Brandy", "oz": 1.5, "ml": 40},
            {"name": "1 oz (30 ml) Orange Liqueur (Cointreau)", "oz": 1.0, "ml": 30},
            {"name": "1 oz (30 ml) Fresh Lemon Juice", "oz": 1.0, "ml": 30},
            {"name": "Sugar for rim (optional)", "oz": 0.0, "ml": 0.0}
        ],
        "tasting_profile": {
            "alcohol": 4,
            "bitter": 1,
            "sour": 3,
            "sweet": 3
        },
        "method": [
            "Prepare: If desired, rim a chilled coupe glass with sugar.",
            "Ice: Fill your cocktail shaker with cubed ice.",
            "Add ingredients: Pour in the Cognac, orange liqueur, and lemon juice.",
            "Shake: Close the shaker and shake hard for 10-15 seconds.",
            "Strain: Double-strain into the prepared coupe glass.",
            "Garnish and serve: Garnish with a lemon or orange twist."
        ],
        "tip": "The balance is key. A classic \"French School\" recipe uses equal parts, but that can be too sweet. Start with this recipe and adjust the lemon juice and liqueur to your taste. A sugar rim can help balance the sourness."
    }
]


def get_mock_recipes() -> List[Dict]:
    return MOCK_RECIPES.copy()

