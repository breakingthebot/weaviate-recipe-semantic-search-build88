"""
Weaviate Semantic and Hybrid Search REST Routes.
Exposes nearText conceptual recipe queries and BM25 hybrid search endpoints.
"""

from fastapi import APIRouter

from src.models.schema import (
    WeaviateNearTextQuery,
    WeaviateHybridQuery,
    RecipeSearchResponse,
)
from src.services.recipe_service import get_recipe_service

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])
service = get_recipe_service()


@router.post("/semantic", response_model=RecipeSearchResponse)
def search_semantic_near_text(payload: WeaviateNearTextQuery) -> RecipeSearchResponse:
    """
    Executes Weaviate nearText search finding recipes by descriptive flavor concepts rather than keywords.
    """
    return service.semantic_search(request=payload)


@router.post("/hybrid", response_model=RecipeSearchResponse)
def search_hybrid(payload: WeaviateHybridQuery) -> RecipeSearchResponse:
    """
    Executes Weaviate hybrid search blending nearText semantic vectors and BM25 term matching.
    """
    return service.hybrid_search(request=payload)
