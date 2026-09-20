"""
Build 88 — Weaviate Recipe Semantic Search Engine
Test Configuration & Shared Fixtures
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.engine.weaviate_client import reset_weaviate_engine
from src.services.recipe_service import get_recipe_service


@pytest.fixture(autouse=True)
def isolated_weaviate():
    """
    Guarantees clean state before each test execution
    by resetting the engine and seeding standard catalog recipes.
    """
    reset_weaviate_engine()
    service = get_recipe_service()
    service.seed_default_recipes(force=True)
    yield
    reset_weaviate_engine()


@pytest.fixture
def client():
    """
    FastAPI HTTP test client fixture.
    """
    return TestClient(app)
