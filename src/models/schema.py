"""
Pydantic Schemas for Weaviate Recipe Vector Search Engine.
Defines recipe models, nearText vector queries, hybrid filters, and chef recommendations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """
    Core Recipe model representing an object stored in Weaviate.
    """

    id: str = Field(..., description="Unique UUID for recipe object")
    title: str = Field(..., min_length=2, max_length=200, description="Recipe name")
    description: str = Field(..., min_length=10, description="Descriptive culinary profile, flavors, and textures")
    ingredients: List[str] = Field(default_factory=list, description="List of raw ingredients")
    cuisine: str = Field(..., min_length=2, max_length=64, description="Culinary origin (e.g. Italian, Thai, Mexican)")
    dietary_tags: List[str] = Field(default_factory=list, description="Dietary compatibility (e.g. keto, gluten-free, vegan)")
    prep_time_minutes: int = Field(default=15, ge=1, le=600, description="Preparation duration in minutes")
    cook_time_minutes: int = Field(default=20, ge=0, le=1440, description="Cooking duration in minutes")
    servings: int = Field(default=4, ge=1, le=100, description="Yield servings count")
    calories_per_serving: int = Field(default=450, ge=10, le=5000, description="Estimated calories per portion")
    difficulty: str = Field(default="Medium", description="Skill level: Easy, Medium, Hard")
    instructions: List[str] = Field(default_factory=list, description="Step-by-step preparation directions")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")


class RecipeCreateRequest(BaseModel):
    """
    Schema for adding a new recipe into Weaviate.
    """

    title: str = Field(..., min_length=2, max_length=200, description="Recipe title")
    description: str = Field(..., min_length=10, description="Rich sensory description of taste, aromas, and mouthfeel")
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredients")
    cuisine: str = Field(..., min_length=2, max_length=64, description="Cuisine region")
    dietary_tags: Optional[List[str]] = Field(default_factory=list, description="Dietary tags")
    prep_time_minutes: Optional[int] = Field(default=15, ge=1)
    cook_time_minutes: Optional[int] = Field(default=20, ge=0)
    servings: Optional[int] = Field(default=4, ge=1)
    calories_per_serving: Optional[int] = Field(default=450, ge=10)
    difficulty: Optional[str] = Field(default="Medium")
    instructions: Optional[List[str]] = Field(default_factory=list)


class RecipeResponse(BaseModel):
    """
    Response schema returning a created or retrieved recipe.
    """

    recipe: Recipe
    status: str = "success"


class WeaviateNearTextQuery(BaseModel):
    """
    Weaviate nearText semantic search query schema.
    Retrieves recipes by conceptual description rather than exact keyword matches.
    """

    concepts: List[str] = Field(..., min_length=1, description="Natural language search concepts or flavor descriptions")
    certainty: Optional[float] = Field(default=0.50, ge=0.0, le=1.0, description="Minimum Weaviate certainty cutoff")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of objects to return")
    where: Optional[Dict[str, Any]] = Field(default=None, description="Weaviate GraphQL where filter dictionary")


class WeaviateHybridQuery(BaseModel):
    """
    Weaviate hybrid search combining nearText semantic vectors with BM25 keyword matching.
    """

    query: str = Field(..., min_length=1, description="Natural language search phrase")
    alpha: float = Field(default=0.75, ge=0.0, le=1.0, description="1.0 = pure vector nearText, 0.0 = pure BM25 keyword")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of objects to return")
    where: Optional[Dict[str, Any]] = Field(default=None, description="Weaviate GraphQL where filter dictionary")


class ScoredRecipeMatch(BaseModel):
    """
    Retrieved recipe match with Weaviate vector metrics.
    """

    id: str
    recipe: Recipe
    certainty: float = Field(..., description="Weaviate certainty metric (0.0 to 1.0, higher is closer)")
    distance: float = Field(..., description="Cosine angular distance (0.0 to 2.0, lower is closer)")
    score: float = Field(..., description="Normalized overall ranking score")


class RecipeSearchResponse(BaseModel):
    """
    Search results response containing ranked recipes and execution telemetry.
    """

    query: str
    search_mode: str
    total_results: int
    matches: List[ScoredRecipeMatch]
    processing_time_ms: float


class ChefRecommendationRequest(BaseModel):
    """
    Request for generative culinary suggestions based on flavor cravings and constraints.
    """

    craving_description: str = Field(..., min_length=3, description="What the diner is in the mood for")
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list, description="Dietary constraints (e.g. keto, vegan)")
    max_prep_time_minutes: Optional[int] = Field(default=None, ge=5, description="Maximum prep time in minutes")


class ChefRecommendationResponse(BaseModel):
    """
    Synthesized chef pairing advice and recommended recipe.
    """

    craving: str
    recommendation_text: str
    top_recipe: Recipe
    pairing_suggestion: str
    substitution_tips: List[str]
    confidence_score: float
    processing_time_ms: float


class WeaviateClassSchemaResponse(BaseModel):
    """
    Weaviate class schema telemetry response.
    """

    class_name: str
    description: str
    vector_index_type: str
    distance_metric: str
    total_objects: int
    properties: List[Dict[str, Any]]
