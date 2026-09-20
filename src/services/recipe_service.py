"""
Recipe Management and Culinary Semantic Search Service.
Coordinates Weaviate object persistence, dataset seeding, nearText semantic search,
and generative chef pairing recommendations.
"""

import time
from typing import List, Optional, Dict, Any

from src.config import settings
from src.engine.weaviate_client import get_weaviate_engine
from src.models.schema import (
    Recipe,
    RecipeCreateRequest,
    WeaviateNearTextQuery,
    WeaviateHybridQuery,
    RecipeSearchResponse,
    ChefRecommendationRequest,
    ChefRecommendationResponse,
)
from src.services.recipe_seed_data import SEED_RECIPES


class RecipeService:
    """
    Business logic layer for recipe semantic retrieval, catalog indexing, and chef recommendations.
    """

    def __init__(self) -> None:
        self.engine = get_weaviate_engine()
        self.seed_default_recipes()

    def seed_default_recipes(self, force: bool = False) -> int:
        """
        Populates Weaviate with the rich seed recipe dataset if empty.
        """
        if len(self.engine.objects) > 0 and not force:
            return 0

        count = 0
        for item in SEED_RECIPES:
            self.engine.create_object(
                properties=item,
                object_id=item["id"],
            )
            count += 1

        return count

    def create_recipe(self, request: RecipeCreateRequest) -> Recipe:
        """
        Ingests a new recipe into Weaviate, calculating dense culinary vectors.
        """
        props = request.model_dump()
        return self.engine.create_object(properties=props)

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieves a single recipe by its unique ID.
        """
        return self.engine.get_object(object_id=recipe_id)

    def list_recipes(
        self,
        limit: int = 50,
        offset: int = 0,
        cuisine: Optional[str] = None,
        dietary_tag: Optional[str] = None,
    ) -> List[Recipe]:
        """
        Lists stored recipes with optional cuisine and dietary filters.
        """
        recipes = self.engine.list_objects(limit=limit, offset=offset)

        if cuisine:
            cuisine_lower = cuisine.lower()
            recipes = [r for r in recipes if r.cuisine.lower() == cuisine_lower]

        if dietary_tag:
            tag_lower = dietary_tag.lower()
            recipes = [
                r for r in recipes
                if any(tag_lower == t.lower() for t in r.dietary_tags)
            ]

        return recipes

    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Deletes a recipe object from Weaviate.
        """
        return self.engine.delete_object(object_id=recipe_id)

    def semantic_search(self, request: WeaviateNearTextQuery) -> RecipeSearchResponse:
        """
        Executes Weaviate nearText semantic search using sensory description concepts.
        """
        start_time = time.perf_counter()

        matches = self.engine.query_near_text(
            concepts=request.concepts,
            certainty=request.certainty or settings.DEFAULT_CERTAINTY_THRESHOLD,
            limit=request.limit or settings.DEFAULT_SEARCH_LIMIT,
            where=request.where,
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        query_text = " ".join(request.concepts)

        return RecipeSearchResponse(
            query=query_text,
            search_mode="nearText",
            total_results=len(matches),
            matches=matches,
            processing_time_ms=duration_ms,
        )

    def hybrid_search(self, request: WeaviateHybridQuery) -> RecipeSearchResponse:
        """
        Executes Weaviate hybrid search blending semantic nearText and BM25 keywords.
        """
        start_time = time.perf_counter()

        matches = self.engine.query_hybrid(
            query=request.query,
            alpha=request.alpha,
            limit=request.limit or settings.DEFAULT_SEARCH_LIMIT,
            where=request.where,
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return RecipeSearchResponse(
            query=request.query,
            search_mode="hybrid",
            total_results=len(matches),
            matches=matches,
            processing_time_ms=duration_ms,
        )

    def get_chef_recommendation(self, request: ChefRecommendationRequest) -> ChefRecommendationResponse:
        """
        Synthesizes a personalized culinary recommendation and beverage pairing
        matching the diner's flavor cravings and constraints.
        """
        start_time = time.perf_counter()

        # Build Weaviate filter if constraints are specified
        where_filter: Optional[Dict[str, Any]] = None
        filter_operands: List[Dict[str, Any]] = []

        if request.dietary_restrictions:
            filter_operands.append({
                "path": ["dietary_tags"],
                "operator": "ContainsAny",
                "valueTextArray": request.dietary_restrictions,
            })

        if request.max_prep_time_minutes:
            filter_operands.append({
                "path": ["prep_time_minutes"],
                "operator": "LessThanEqual",
                "valueInt": request.max_prep_time_minutes,
            })

        if len(filter_operands) == 1:
            where_filter = filter_operands[0]
        elif len(filter_operands) > 1:
            where_filter = {
                "operator": "And",
                "operands": filter_operands,
            }

        # Search top candidate recipes
        matches = self.engine.query_near_text(
            concepts=[request.craving_description],
            certainty=0.40,
            limit=3,
            where=where_filter,
        )

        # Fallback if no matching recipe met constraints
        if not matches:
            fallback_recipes = self.engine.list_objects(limit=1)
            top_rec = fallback_recipes[0]
            confidence = 0.50
        else:
            top_rec = matches[0].recipe
            confidence = matches[0].certainty

        # Formulate pairing suggestions based on cuisine and flavor profile
        cuisine = top_rec.cuisine
        if cuisine == "Italian":
            pairing = "Pair with a crisp, acidic Pinot Grigio or medium-bodied Chianti Classico to balance rich cream and garlic."
            subs = [
                "Swap heavy cream for coconut cream or cashew milk for a dairy-free variation.",
                "Use nutritional yeast instead of parmesan cheese to maintain savory umami."
            ]
        elif cuisine == "Mexican":
            pairing = "Serve with ice-cold Mexican lager with lime or a refreshing smoked mezcal paloma."
            subs = [
                "Substitute grilled king oyster mushrooms or jackfruit for a vegetarian carnitas.",
                "Use bibb lettuce leaves instead of corn tortillas for an ultra-low-carb wrap."
            ]
        elif cuisine == "Thai":
            pairing = "Pair with chilled off-dry German Riesling or refreshing Thai iced tea with coconut milk."
            subs = [
                "Substitute tamari or coconut aminos if avoiding fermented fish sauce.",
                "Tofu cubes or seitan absorb the spicy lemongrass broth wonderfully."
            ]
        elif cuisine == "Indian":
            pairing = "Enjoy alongside garlic naan, basmati rice, and a chilled mango lassi."
            subs = [
                "Use coconut yogurt and coconut cream for a rich dairy-free butter sauce.",
                "Replace chicken thighs with paneer cheese or roasted cauliflower florets."
            ]
        elif cuisine == "French":
            pairing = "Pair with a glass of late-harvest Sauternes or an espresso shot."
            subs = [
                "Use coconut sugar or monkfruit sweetener for lower glycemic caramelization.",
                "A pinch of cardamom or lavender flowers adds floral complexity."
            ]
        else:
            pairing = "Pair with sparkling mineral water with fresh lemon or a crisp Sauvignon Blanc."
            subs = [
                "Substitute extra-virgin olive oil for butter.",
                "Increase fresh herbs like dill, tarragon, or chives for aromatic brightness."
            ]

        recommendation_text = (
            f"Chef Recommends: '{top_rec.title}' ({top_rec.cuisine}). "
            f"{top_rec.description} This dish delivers exactly the flavor profile you are craving."
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return ChefRecommendationResponse(
            craving=request.craving_description,
            recommendation_text=recommendation_text,
            top_recipe=top_rec,
            pairing_suggestion=pairing,
            substitution_tips=subs,
            confidence_score=confidence,
            processing_time_ms=duration_ms,
        )


_recipe_service_instance: Optional[RecipeService] = None


def get_recipe_service() -> RecipeService:
    """
    Returns the singleton recipe service.
    """
    global _recipe_service_instance
    if _recipe_service_instance is None:
        _recipe_service_instance = RecipeService()
    return _recipe_service_instance
