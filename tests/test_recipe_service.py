"""
Build 88 — Weaviate Recipe Semantic Search Engine
Unit Tests for RecipeService Business Logic
"""

import pytest

from src.services.recipe_service import get_recipe_service
from src.models.schema import (
    RecipeCreateRequest,
    WeaviateNearTextQuery,
    WeaviateHybridQuery,
    ChefRecommendationRequest,
)


def test_seed_catalog_count():
    """
    Verifies that the catalog seeds all default authentic recipes.
    """
    svc = get_recipe_service()
    count = svc.seed_default_recipes(force=True)
    assert count == 8

    recipes = svc.list_recipes()
    assert len(recipes) == 8


def test_add_and_get_recipe():
    """
    Verifies adding a custom recipe into the catalog and retrieving it.
    """
    svc = get_recipe_service()
    req = RecipeCreateRequest(
        title="Smoked Brisket Quesadillas",
        cuisine="Mexican",
        prep_time_minutes=15,
        cook_time_minutes=10,
        calories_per_serving=650,
        dietary_tags=["high-protein"],
        ingredients=["smoked brisket", "monterey jack cheese", "flour tortillas", "pico de gallo"],
        description="Crisp toasted flour tortillas overflowing with tender smoked beef brisket and molten cheese.",
        difficulty="Medium"
    )
    created = svc.create_recipe(req)
    assert created.id is not None
    assert created.title == "Smoked Brisket Quesadillas"

    fetched = svc.get_recipe(created.id)
    assert fetched is not None
    assert fetched.title == created.title


def test_search_by_sensory_description_filtering():
    """
    Tests nearText sensory description searching with cuisine and dietary filters.
    """
    svc = get_recipe_service()
    where_filter = {"operator": "Equal", "path": ["cuisine"], "valueText": "Italian"}
    query = WeaviateNearTextQuery(
        concepts=["warm comforting creamy garlic pasta"],
        limit=5,
        certainty=0.40,
        where=where_filter,
    )
    res = svc.semantic_search(query)
    assert res.total_results > 0
    assert res.matches[0].recipe.cuisine == "Italian"
    top_title = res.matches[0].recipe.title.lower()
    top_desc = res.matches[0].recipe.description.lower()
    assert ("garlic" in top_title or "chicken" in top_title or "fettuccine" in top_title or "parmesan" in top_desc or "cream" in top_desc)


def test_search_with_dietary_restriction():
    """
    Tests searching recipes constrained by dietary tags (e.g. keto or gluten-free).
    """
    svc = get_recipe_service()
    where_filter = {"operator": "ContainsAny", "path": ["dietary_tags"], "valueText": "gluten-free"}
    query = WeaviateNearTextQuery(
        concepts=["delicious hearty dinner"],
        limit=5,
        certainty=0.30,
        where=where_filter,
    )
    res = svc.semantic_search(query)
    assert res.total_results > 0
    for match in res.matches:
        assert "gluten-free" in [t.lower() for t in match.recipe.dietary_tags]


def test_chef_recommendation_flow():
    """
    Tests generative chef agent recommendation, beverage pairing, and smart substitutions.
    """
    svc = get_recipe_service()
    req = ChefRecommendationRequest(
        craving_description="I want something rich, creamy, and decadent for date night, but low carb",
        dietary_restrictions=["keto"]
    )
    rec = svc.get_chef_recommendation(req)

    assert rec.top_recipe is not None
    assert rec.confidence_score > 0.4
    assert len(rec.recommendation_text) > 10
    assert len(rec.pairing_suggestion) > 5
    assert isinstance(rec.substitution_tips, list)


def test_delete_recipe_from_service():
    """
    Tests deleting a recipe by ID and confirming removal.
    """
    svc = get_recipe_service()
    req = RecipeCreateRequest(
        title="Disposable Salad",
        cuisine="American",
        prep_time_minutes=5,
        cook_time_minutes=0,
        calories_per_serving=150,
        dietary_tags=["vegan"],
        ingredients=["lettuce", "cucumber"],
        description="Simple fresh chopped greens"
    )
    created = svc.create_recipe(req)
    assert svc.get_recipe(created.id) is not None

    deleted = svc.delete_recipe(created.id)
    assert deleted is True
    assert svc.get_recipe(created.id) is None
