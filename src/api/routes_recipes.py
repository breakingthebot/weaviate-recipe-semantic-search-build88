"""
Recipe Catalog and Chef Recommendation REST Routes.
Handles recipe CRUD, dietary filtering, and generative pairing recommendations.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

from src.models.schema import (
    Recipe,
    RecipeCreateRequest,
    RecipeResponse,
    ChefRecommendationRequest,
    ChefRecommendationResponse,
)
from src.services.recipe_service import get_recipe_service

router = APIRouter(prefix="/api/recipes", tags=["Recipe Management"])
service = get_recipe_service()


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreateRequest) -> RecipeResponse:
    """
    Creates a new recipe and indexes its culinary vector embedding in Weaviate.
    """
    created = service.create_recipe(request=payload)
    return RecipeResponse(recipe=created, status="created")


@router.get("", response_model=List[Recipe])
def list_recipes(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    cuisine: Optional[str] = Query(default=None, description="Filter by cuisine region"),
    dietary_tag: Optional[str] = Query(default=None, description="Filter by dietary tag (e.g. keto, vegan)"),
) -> List[Recipe]:
    """
    Lists recipes stored in Weaviate with optional pagination and filters.
    """
    return service.list_recipes(
        limit=limit,
        offset=offset,
        cuisine=cuisine,
        dietary_tag=dietary_tag,
    )


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: str) -> Recipe:
    """
    Retrieves recipe details by its unique identifier.
    """
    recipe = service.get_recipe(recipe_id=recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe '{recipe_id}' not found",
        )
    return recipe


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: str) -> Dict[str, Any]:
    """
    Deletes a recipe from Weaviate by its ID.
    """
    deleted = service.delete_recipe(recipe_id=recipe_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe '{recipe_id}' not found",
        )
    return {"ok": True, "deleted": recipe_id}


@router.post("/recommend", response_model=ChefRecommendationResponse)
def get_chef_recommendation(payload: ChefRecommendationRequest) -> ChefRecommendationResponse:
    """
    Generates personalized chef advice, recipe matches, and beverage pairings based on sensory cravings.
    """
    return service.get_chef_recommendation(request=payload)
