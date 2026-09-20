"""
Culinary Recipe Seed Dataset for Weaviate Semantic Search.
Provides authentic recipes with rich flavor descriptions, dietary tags, and ingredient profiles.
"""

from typing import List, Dict, Any

SEED_RECIPES: List[Dict[str, Any]] = [
    {
        "id": "rec_tuscan_chicken",
        "title": "Creamy Tuscan Garlic Chicken",
        "description": "Pan-seared tender chicken breasts bathed in a velvety garlic parmesan cream sauce infused with wilted baby spinach and sweet tangy sun-dried tomatoes. Comforting, rich, and homestyle.",
        "ingredients": ["chicken breast", "heavy cream", "parmesan cheese", "sun-dried tomatoes", "baby spinach", "garlic", "olive oil", "fresh basil"],
        "cuisine": "Italian",
        "dietary_tags": ["keto", "low-carb", "gluten-free"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "calories_per_serving": 520,
        "difficulty": "Easy",
        "instructions": [
            "Season chicken with salt, pepper, and Italian herbs.",
            "Sear in olive oil over medium-high heat until golden brown.",
            "Remove chicken, sauté minced garlic and sun-dried tomatoes.",
            "Stir in heavy cream and grated parmesan until velvety.",
            "Add spinach to wilt, then return chicken to simmer."
        ],
    },
    {
        "id": "rec_al_pastor_tacos",
        "title": "Smoky Street Tacos Al Pastor",
        "description": "Thinly sliced pork marinated in smoky guajillo chilies, achiote paste, and pineapple juice, seared with caramelized pineapple chunks and served on warm corn tortillas with chopped cilantro and diced white onion.",
        "ingredients": ["pork shoulder", "guajillo chilies", "achiote paste", "fresh pineapple", "corn tortillas", "white onion", "cilantro", "lime"],
        "cuisine": "Mexican",
        "dietary_tags": ["gluten-free", "dairy-free"],
        "prep_time_minutes": 30,
        "cook_time_minutes": 25,
        "servings": 6,
        "calories_per_serving": 380,
        "difficulty": "Medium",
        "instructions": [
            "Puree guajillo chilies, achiote, garlic, and pineapple juice.",
            "Marinate pork slices for at least 2 hours.",
            "Grill or sear pork and pineapple slices until charred.",
            "Chop pork and assemble tacos on warm corn tortillas."
        ],
    },
    {
        "id": "rec_tom_yum_goong",
        "title": "Spicy Thai Tom Yum Soup with Jumbo Shrimp",
        "description": "An intoxicating hot and sour lemongrass broth brimming with succulent jumbo shrimp, straw mushrooms, fragrant kaffir lime leaves, galangal, and crushed Thai bird chilies with a squeeze of fresh lime juice.",
        "ingredients": ["jumbo shrimp", "lemongrass", "kaffir lime leaves", "galangal", "straw mushrooms", "thai bird chilies", "fish sauce", "lime juice", "cilantro"],
        "cuisine": "Thai",
        "dietary_tags": ["gluten-free", "dairy-free", "low-carb", "keto"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "servings": 4,
        "calories_per_serving": 210,
        "difficulty": "Easy",
        "instructions": [
            "Simmer shrimp stock with smashed lemongrass, galangal, and kaffir lime.",
            "Add mushrooms and bruised bird eye chilies.",
            "Add shrimp and cook gently until pink and opaque.",
            "Remove from heat and stir in lime juice and fish sauce."
        ],
    },
    {
        "id": "rec_butter_chicken",
        "title": "Authentic Murgh Makhani Butter Chicken",
        "description": "Tender tandoori-spiced chicken thighs simmered in a luscious, silky tomato sauce enriched with butter, heavy cream, aromatic fenugreek leaves (kasuri methi), and warm garam masala spices.",
        "ingredients": ["chicken thighs", "greek yogurt", "garam masala", "crushed tomatoes", "butter", "heavy cream", "ginger garlic paste", "kasuri methi"],
        "cuisine": "Indian",
        "dietary_tags": ["gluten-free", "keto"],
        "prep_time_minutes": 25,
        "cook_time_minutes": 35,
        "servings": 4,
        "calories_per_serving": 590,
        "difficulty": "Medium",
        "instructions": [
            "Marinate chicken in yogurt and spices, then broil until charred.",
            "Melt butter and sauté ginger garlic paste with whole spices.",
            "Simmer pureed tomatoes and blend until completely smooth.",
            "Stir in cream, fenugreek leaves, and tandoori chicken."
        ],
    },
    {
        "id": "rec_mediterranean_salmon",
        "title": "Pan-Seared Wild Salmon Piccata",
        "description": "Crispy-skinned wild Alaskan salmon fillets served over a bright, herbaceous pan sauce made with browned butter, white wine, zesty lemon juice, and briny capers with fresh Italian flat-leaf parsley.",
        "ingredients": ["wild salmon fillets", "capers", "unsalted butter", "fresh lemon", "white wine", "garlic", "olive oil", "fresh parsley"],
        "cuisine": "Mediterranean",
        "dietary_tags": ["keto", "gluten-free", "low-carb"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 12,
        "servings": 2,
        "calories_per_serving": 420,
        "difficulty": "Easy",
        "instructions": [
            "Sear salmon skin-side down in hot olive oil until crispy.",
            "Flip briefly to finish cooking and transfer to plate.",
            "In the same skillet, deglaze with wine, lemon juice, and capers.",
            "Swirl in cold butter cubes to emulsify sauce and spoon over salmon."
        ],
    },
    {
        "id": "rec_vegan_buddha_bowl",
        "title": "Roasted Chickpea Green Goddess Buddha Bowl",
        "description": "A vibrant, wholesome vegan bowl piled high with crispy cumin-roasted chickpeas, quinoa, roasted sweet potatoes, sliced avocado, shaved radishes, and drizzled with an herbaceous green tahini dressing.",
        "ingredients": ["chickpeas", "quinoa", "sweet potato", "avocado", "tahini", "lemon juice", "baby kale", "hemp hearts", "cumin"],
        "cuisine": "American",
        "dietary_tags": ["vegan", "vegetarian", "gluten-free", "dairy-free"],
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "servings": 2,
        "calories_per_serving": 480,
        "difficulty": "Easy",
        "instructions": [
            "Roast spiced chickpeas and diced sweet potato until golden.",
            "Cook fluffy quinoa in vegetable broth.",
            "Whisk tahini, lemon juice, garlic, and fresh herbs into dressing.",
            "Assemble bowls with greens, grains, roasted legumes, and avocado."
        ],
    },
    {
        "id": "rec_classic_creme_brulee",
        "title": "Classic Vanilla Bean Crème Brûlée",
        "description": "An indulgent, silky French custard infused with real Madagascar vanilla bean caviar, baked to gentle perfection and topped with a brittle, crackling layer of golden caramelized sugar.",
        "ingredients": ["heavy cream", "egg yolks", "granulated sugar", "vanilla bean pod", "pinch of sea salt"],
        "cuisine": "French",
        "dietary_tags": ["vegetarian", "gluten-free"],
        "prep_time_minutes": 20,
        "cook_time_minutes": 45,
        "servings": 6,
        "calories_per_serving": 410,
        "difficulty": "Hard",
        "instructions": [
            "Steep split vanilla bean pod and seeds in heated heavy cream.",
            "Whisk egg yolks and sugar until pale and thick.",
            "Slowly temper hot cream into yolks, strain into ramekins.",
            "Bake in a water bath at 300°F until edges set with a slight wobble.",
            "Chill thoroughly, sprinkle sugar on top, and torch until brittle."
        ],
    },
    {
        "id": "rec_miso_ramen",
        "title": "Rich Spicy Miso Pork Ramen",
        "description": "Steaming bowl of rich pork bone tonkotsu broth emulsified with fermented red and white miso paste, spicy chili sesame oil, tender springy wheat noodles, melt-in-your-mouth braised chashu pork belly, and a soft-boiled jammy soy egg.",
        "ingredients": ["pork bone broth", "red miso paste", "chili sesame oil", "ramen noodles", "chashu pork belly", "soft boiled egg", "scallions", "nori seaweed"],
        "cuisine": "Japanese",
        "dietary_tags": ["dairy-free"],
        "prep_time_minutes": 30,
        "cook_time_minutes": 40,
        "servings": 2,
        "calories_per_serving": 680,
        "difficulty": "Medium",
        "instructions": [
            "Whisk miso paste, garlic, and chili oil into piping hot tonkotsu broth.",
            "Boil fresh ramen noodles for exactly 90 seconds until al dente.",
            "Place noodles in bowl, pour broth, and top with seared chashu.",
            "Garnish with halved ajitsuke tamago, scallions, and nori."
        ],
    }
]
