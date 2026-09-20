"""
Build 88 — Weaviate Recipe Semantic Search Engine
Unit Tests for MemoryWeaviate Engine
"""

import pytest

from src.engine.memory_weaviate import MemoryWeaviate
from src.engine.embedder import get_culinary_embedder


def test_create_and_get_object():
    """
    Tests inserting a data object into Weaviate memory engine and retrieving it by UUID.
    """
    engine = MemoryWeaviate()
    props = {
        "title": "Tuscan Garlic Chicken",
        "cuisine": "Italian",
        "difficulty": "Easy",
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "calories_per_serving": 520,
        "dietary_tags": ["keto", "gluten-free"],
        "ingredients": ["chicken breast", "heavy cream", "garlic", "spinach", "sun-dried tomatoes"],
        "description": "Pan-seared chicken bathed in rich garlic parmesan cream sauce."
    }
    recipe_obj = engine.create_object(properties=props)

    assert recipe_obj.id is not None
    fetched = engine.get_object(object_id=recipe_obj.id)
    assert fetched is not None
    assert fetched.title == "Tuscan Garlic Chicken"
    assert fetched.cuisine == "Italian"


def test_delete_object():
    """
    Tests deleting an object by UUID.
    """
    engine = MemoryWeaviate()
    props = {"title": "Temp Recipe", "cuisine": "General", "description": "Quick snack"}
    recipe_obj = engine.create_object(properties=props)

    assert engine.get_object(object_id=recipe_obj.id) is not None
    deleted = engine.delete_object(object_id=recipe_obj.id)
    assert deleted is True
    assert engine.get_object(object_id=recipe_obj.id) is None

    # Deleting again returns False
    assert engine.delete_object(object_id=recipe_obj.id) is False


def test_list_objects():
    """
    Tests paginated object listing from Weaviate storage.
    """
    engine = MemoryWeaviate()
    for i in range(5):
        engine.create_object(properties={"title": f"Dish {i}", "cuisine": "Fusion", "description": f"Dish {i} description"})

    items = engine.list_objects(limit=3, offset=0)
    assert len(items) == 3

    items_next = engine.list_objects(limit=3, offset=3)
    assert len(items_next) == 2


def test_query_near_text():
    """
    Tests semantic nearText search calculating certainty and distance.
    """
    engine = MemoryWeaviate()
    r1 = {
        "title": "Spicy Thai Tom Yum",
        "cuisine": "Thai",
        "description": "Fiery lemongrass, kaffir lime, chili broth with plump shrimp"
    }
    r2 = {
        "title": "Vanilla Panna Cotta",
        "cuisine": "Italian",
        "description": "Chilled silky sweet vanilla cream dessert with berries"
    }
    engine.create_object(properties=r1)
    engine.create_object(properties=r2)

    matches = engine.query_near_text(concepts=["fiery spicy lemongrass soup"], certainty=0.30, limit=2)

    assert len(matches) == 2
    # First match must be Tom Yum
    assert matches[0].recipe.title == "Spicy Thai Tom Yum"
    assert matches[0].certainty > matches[1].certainty
    assert matches[0].distance < matches[1].distance


def test_query_hybrid_blending():
    """
    Tests hybrid search combining BM25 keyword matching and vector similarity.
    """
    engine = MemoryWeaviate()
    r1 = {
        "title": "Matcha Green Tea Cake",
        "cuisine": "Japanese",
        "description": "Earthy bittersweet sponge cake"
    }
    r2 = {
        "title": "Lemongrass Coconut Chicken",
        "cuisine": "Thai",
        "description": "Tangy aromatic broth"
    }
    engine.create_object(properties=r1)
    engine.create_object(properties=r2)

    # Test pure BM25 keywords (alpha=0.0)
    bm25_matches = engine.query_hybrid(query="Matcha", alpha=0.0, limit=2)
    assert len(bm25_matches) > 0
    assert bm25_matches[0].recipe.title == "Matcha Green Tea Cake"

    # Test pure vector search (alpha=1.0)
    vector_matches = engine.query_hybrid(query="earthy sweet dessert", alpha=1.0, limit=2)
    assert len(vector_matches) > 0
    assert vector_matches[0].recipe.title == "Matcha Green Tea Cake"


def test_where_filters_complex():
    """
    Tests where filtering with Equal, GreaterThan, ContainsAny, and Or logic.
    """
    engine = MemoryWeaviate()
    engine.create_object(properties={
        "title": "Quick Tacos",
        "cuisine": "Mexican",
        "description": "Quick street food tacos",
        "prep_time_minutes": 10,
        "dietary_tags": ["gluten-free", "dairy-free"]
    })
    engine.create_object(properties={
        "title": "Slow Braised Osso Buco",
        "cuisine": "Italian",
        "description": "Tender braised veal shanks",
        "prep_time_minutes": 45,
        "dietary_tags": ["keto"]
    })

    # Filter by cuisine Equal
    cuisine_filter = {"operator": "Equal", "path": ["cuisine"], "valueText": "Mexican"}
    results = engine.query_near_text(concepts=["food"], certainty=0.0, where=cuisine_filter)
    assert len(results) == 1
    assert results[0].recipe.title == "Quick Tacos"

    # Filter by prep_time_minutes GreaterThan 20
    time_filter = {"operator": "GreaterThan", "path": ["prep_time_minutes"], "valueInt": 20}
    results_time = engine.query_near_text(concepts=["food"], certainty=0.0, where=time_filter)
    assert len(results_time) == 1
    assert results_time[0].recipe.title == "Slow Braised Osso Buco"

    # Filter with ContainsAny on dietary_tags
    diet_filter = {"operator": "ContainsAny", "path": ["dietary_tags"], "valueText": "gluten-free"}
    results_diet = engine.query_near_text(concepts=["food"], certainty=0.0, where=diet_filter)
    assert len(results_diet) == 1
    assert results_diet[0].recipe.title == "Quick Tacos"


def test_reset_clears_all_objects():
    """
    Tests resetting engine purges all stored objects.
    """
    engine = MemoryWeaviate()
    engine.create_object(properties={
        "title": "Temporary Bowl",
        "cuisine": "Hawaiian",
        "description": "Fresh ahi poke bowl with edamame and sesame"
    })
    assert len(engine.objects) == 1

    engine.reset()
    assert len(engine.objects) == 0


def test_where_filter_not_equal_and_compound():
    """
    Tests NotEqual and compound And/Or filters.
    """
    engine = MemoryWeaviate()
    engine.create_object(properties={
        "title": "Ramen",
        "cuisine": "Japanese",
        "description": "Savory ramen noodles in rich pork bone broth"
    })
    engine.create_object(properties={
        "title": "Pasta",
        "cuisine": "Italian",
        "description": "Classic pasta with rich herb tomato marinara"
    })
    engine.create_object(properties={
        "title": "Pho",
        "cuisine": "Vietnamese",
        "description": "Fragrant beef broth with rice noodles and basil"
    })

    # NotEqual
    not_equal_filter = {"operator": "NotEqual", "path": ["cuisine"], "valueText": "Japanese"}
    res_not = engine.query_near_text(concepts=["noodles"], certainty=0.0, where=not_equal_filter)
    assert len(res_not) == 2
    assert all(m.recipe.cuisine != "Japanese" for m in res_not)

    # Compound Or
    compound_or = {
        "operator": "Or",
        "operands": [
            {"operator": "Equal", "path": ["cuisine"], "valueText": "Italian"},
            {"operator": "Equal", "path": ["cuisine"], "valueText": "Vietnamese"}
        ]
    }
    res_or = engine.query_near_text(concepts=["broth"], certainty=0.0, where=compound_or)
    assert len(res_or) == 2
