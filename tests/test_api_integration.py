"""
Build 88 — Weaviate Recipe Semantic Search Engine
Integration Tests for FastAPI REST Endpoints
"""

import pytest


def test_root_discovery_endpoint(client):
    """
    Tests GET / root discovery metadata endpoint.
    """
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["build"] == 88
    assert "Weaviate" in data["technology"]
    assert "endpoints" in data


def test_dashboard_endpoint(client):
    """
    Tests GET /dashboard HTML interface delivery.
    """
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Weaviate Recipe Semantic Search Engine" in res.text


def test_list_recipes_endpoint(client):
    """
    Tests GET /api/recipes retrieving seeded catalog.
    """
    res = client.get("/api/recipes")
    assert res.status_code == 200
    recipes = res.json()
    assert len(recipes) == 8


def test_create_and_delete_recipe_flow(client):
    """
    Tests creating a recipe via POST /api/recipes and deleting via DELETE /api/recipes/{id}.
    """
    payload = {
        "title": "Avocado Citrus Toast",
        "cuisine": "American",
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
        "calories_per_serving": 280,
        "dietary_tags": ["vegan", "dairy-free"],
        "ingredients": ["sourdough bread", "avocado", "lemon juice", "red pepper flakes"],
        "description": "Crisp toasted artisan bread layered with creamy crushed avocado, sea salt, and citrus zest.",
        "difficulty": "Easy"
    }
    create_res = client.post("/api/recipes", json=payload)
    assert create_res.status_code == 201
    created_resp = create_res.json()
    created_recipe = created_resp["recipe"]
    assert created_recipe["title"] == "Avocado Citrus Toast"
    recipe_id = created_recipe["id"]

    # Retrieve
    get_res = client.get(f"/api/recipes/{recipe_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == recipe_id

    # Delete
    del_res = client.delete(f"/api/recipes/{recipe_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] == recipe_id

    # Confirm 404 after deletion
    not_found_res = client.get(f"/api/recipes/{recipe_id}")
    assert not_found_res.status_code == 404


def test_get_nonexistent_recipe(client):
    """
    Tests GET /api/recipes/{id} returns 404 for missing UUID.
    """
    res = client.get("/api/recipes/rec_000000000000")
    assert res.status_code == 404


def test_semantic_search_endpoint(client):
    """
    Tests POST /api/search/semantic nearText sensory description search.
    """
    payload = {
        "concepts": ["fiery hot noodles with garlic and herbs"],
        "limit": 3,
        "certainty": 0.35
    }
    res = client.post("/api/search/semantic", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "matches" in data
    matches = data["matches"]
    assert len(matches) > 0
    first = matches[0]
    assert "recipe" in first
    assert "certainty" in first
    assert "distance" in first
    assert first["certainty"] >= 0.35


def test_semantic_search_with_filters(client):
    """
    Tests POST /api/search/semantic with GraphQL-style where filter.
    """
    where_filter = {
        "operator": "Equal",
        "path": ["cuisine"],
        "valueText": "French"
    }
    payload = {
        "concepts": ["rich vanilla custard dessert"],
        "limit": 5,
        "certainty": 0.30,
        "where": where_filter
    }
    res = client.post("/api/search/semantic", json=payload)
    assert res.status_code == 200
    data = res.json()
    matches = data["matches"]
    for match in matches:
        assert match["recipe"]["cuisine"] == "French"


def test_hybrid_search_endpoint(client):
    """
    Tests POST /api/search/hybrid combining BM25 keyword score and dense vector certainty.
    """
    payload = {
        "query": "tacos cilantro lime",
        "alpha": 0.5,
        "limit": 4
    }
    res = client.post("/api/search/hybrid", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "matches" in data
    matches = data["matches"]
    assert len(matches) > 0
    assert "score" in matches[0]
    assert "certainty" in matches[0]


def test_chef_recommendations_endpoint(client):
    """
    Tests POST /api/recipes/recommend generative chef pairing pipeline.
    """
    payload = {
        "craving_description": "Something spicy, fragrant, and warming with coconut broth",
        "dietary_restrictions": ["dairy-free"],
        "max_prep_time_minutes": 45
    }
    res = client.post("/api/recipes/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "top_recipe" in data
    assert "recommendation_text" in data
    assert "pairing_suggestion" in data
    assert "substitution_tips" in data
    assert data["confidence_score"] > 0


def test_system_schema_endpoint(client):
    """
    Tests GET /api/system/schema class schema metadata inspection.
    """
    res = client.get("/api/system/schema")
    assert res.status_code == 200
    schema = res.json()
    assert schema["class_name"] == "Recipe"
    assert schema["vector_index_type"] == "hnsw"
    assert schema["distance_metric"] == "cosine"
    assert schema["total_objects"] == 8
    assert len(schema["properties"]) >= 8


def test_system_reset_and_seed_endpoints(client):
    """
    Tests POST /api/system/reset and POST /api/system/seed.
    """
    # Reset
    reset_res = client.post("/api/system/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["cleared"] is True

    # Verify zero recipes
    list_res = client.get("/api/recipes")
    assert len(list_res.json()) == 0

    # Reseed
    seed_res = client.post("/api/system/seed")
    assert seed_res.status_code == 200
    assert seed_res.json()["seeded_count"] == 8

    # Verify restored
    list_restored = client.get("/api/recipes")
    assert len(list_restored.json()) == 8


def test_create_recipe_validation_error(client):
    """
    Tests POST /api/recipes with invalid body missing required fields returns 422.
    """
    bad_payload = {"title": "X"}  # Too short title, missing cuisine, description, ingredients
    res = client.post("/api/recipes", json=bad_payload)
    assert res.status_code == 422


def test_list_recipes_pagination(client):
    """
    Tests pagination parameters limit and offset on GET /api/recipes.
    """
    res1 = client.get("/api/recipes?limit=3&offset=0")
    assert res1.status_code == 200
    assert len(res1.json()) == 3

    res2 = client.get("/api/recipes?limit=3&offset=3")
    assert res2.status_code == 200
    assert len(res2.json()) == 3


def test_static_assets_delivery(client):
    """
    Tests GET /static/style.css and GET /static/app.js delivery.
    """
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    assert "text/css" in res_css.headers["content-type"]

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200
    assert "javascript" in res_js.headers["content-type"]
