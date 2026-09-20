"""
Weaviate System and Telemetry REST Routes.
Exposes class schema definitions, object counts, and test state resets.
"""

from typing import Dict, Any
from fastapi import APIRouter

from src.models.schema import WeaviateClassSchemaResponse
from src.engine.weaviate_client import get_weaviate_engine, reset_weaviate_engine
from src.services.recipe_service import get_recipe_service

router = APIRouter(prefix="/api/system", tags=["System & Schema"])


@router.get("/schema", response_model=WeaviateClassSchemaResponse)
def get_class_schema() -> WeaviateClassSchemaResponse:
    """
    Returns Weaviate class schema definition, property types, and index metrics.
    """
    engine = get_weaviate_engine()
    return engine.get_class_schema()


@router.post("/reset")
def reset_system() -> Dict[str, Any]:
    """
    Purges all stored Weaviate objects for test isolation.
    """
    reset_weaviate_engine()
    return {
        "ok": True,
        "cleared": True,
        "message": "Weaviate vector database reset successfully",
    }


@router.post("/seed")
def seed_catalog() -> Dict[str, Any]:
    """
    Reseeds default recipe catalog into Weaviate.
    """
    svc = get_recipe_service()
    count = svc.seed_default_recipes(force=True)
    return {
        "ok": True,
        "seeded_count": count,
        "message": f"Successfully seeded {count} authentic recipes into Weaviate",
    }
