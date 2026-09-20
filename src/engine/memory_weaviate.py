"""
In-Memory Weaviate Vector Database Replica Engine.
Implements Weaviate class schemas, object storage, GraphQL-style nearText semantic search,
hybrid alpha retrieval, and nested boolean filter evaluations.
"""

import uuid
import threading
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from src.config import settings
from src.engine.embedder import get_culinary_embedder
from src.models.schema import (
    Recipe,
    ScoredRecipeMatch,
    WeaviateClassSchemaResponse,
)


class MemoryWeaviate:
    """
    In-memory replica of Weaviate Vector Database.
    Preserves Weaviate schema constraints, nearText concepts search, and certainty scoring.
    """

    def __init__(self, class_name: str = "Recipe") -> None:
        self.class_name = class_name
        self.embedder = get_culinary_embedder()
        self.lock = threading.RLock()

        # Class schema properties definition
        self.schema_properties = [
            {"name": "title", "dataType": ["text"], "description": "Recipe title"},
            {"name": "description", "dataType": ["text"], "description": "Sensory flavor profile and mouthfeel"},
            {"name": "ingredients", "dataType": ["text[]"], "description": "Array of ingredient strings"},
            {"name": "cuisine", "dataType": ["text"], "description": "Regional culinary tradition"},
            {"name": "dietary_tags", "dataType": ["text[]"], "description": "Dietary tags like keto, vegan, gluten-free"},
            {"name": "prep_time_minutes", "dataType": ["int"], "description": "Preparation time"},
            {"name": "cook_time_minutes", "dataType": ["int"], "description": "Cooking time"},
            {"name": "servings", "dataType": ["int"], "description": "Portion yield"},
            {"name": "calories_per_serving", "dataType": ["int"], "description": "Caloric density"},
            {"name": "difficulty", "dataType": ["text"], "description": "Skill level: Easy, Medium, Hard"},
            {"name": "instructions", "dataType": ["text[]"], "description": "Step-by-step instructions"},
        ]

        # In-memory storage: uuid -> { "id": str, "properties": dict, "vector": List[float], "created_at": str }
        self.objects: Dict[str, Dict[str, Any]] = {}

    def _now_iso(self) -> str:
        """
        Returns UTC timestamp in ISO 8601 string format.
        """
        return datetime.now(timezone.utc).isoformat()

    def get_class_schema(self) -> WeaviateClassSchemaResponse:
        """
        Returns Weaviate class schema definition and telemetry.
        """
        with self.lock:
            return WeaviateClassSchemaResponse(
                class_name=self.class_name,
                description="Culinary recipe objects indexed with 128-dimensional dense sensory embeddings",
                vector_index_type="hnsw",
                distance_metric="cosine",
                total_objects=len(self.objects),
                properties=self.schema_properties,
            )

    def create_object(
        self,
        properties: Dict[str, Any],
        object_id: Optional[str] = None,
        custom_vector: Optional[List[float]] = None,
    ) -> Recipe:
        """
        Creates and indexes a new Recipe object into Weaviate.
        Generates dense vector embedding from text properties if not provided.
        """
        with self.lock:
            oid = object_id if object_id else f"rec_{uuid.uuid4().hex[:12]}"
            created_at = self._now_iso()

            # Generate culinary vector embedding combining title, description, and ingredients
            if custom_vector is not None:
                vec = custom_vector
            else:
                title = properties.get("title", "")
                desc = properties.get("description", "")
                cuisine = properties.get("cuisine", "")
                ingredients = " ".join(properties.get("ingredients", []))
                diet = " ".join(properties.get("dietary_tags", []))
                text_to_embed = f"{title}. {desc}. Cuisine: {cuisine}. Ingredients: {ingredients}. Dietary: {diet}"
                vec = self.embedder.embed_text(text_to_embed)

            recipe_obj = Recipe(
                id=oid,
                title=properties.get("title", "Untitled Recipe"),
                description=properties.get("description", ""),
                ingredients=properties.get("ingredients", []),
                cuisine=properties.get("cuisine", "General"),
                dietary_tags=properties.get("dietary_tags", []),
                prep_time_minutes=int(properties.get("prep_time_minutes", 15)),
                cook_time_minutes=int(properties.get("cook_time_minutes", 20)),
                servings=int(properties.get("servings", 4)),
                calories_per_serving=int(properties.get("calories_per_serving", 450)),
                difficulty=properties.get("difficulty", "Medium"),
                instructions=properties.get("instructions", []),
                created_at=created_at,
            )

            self.objects[oid] = {
                "id": oid,
                "recipe": recipe_obj,
                "properties": recipe_obj.model_dump(),
                "vector": vec,
                "created_at": created_at,
            }

            return recipe_obj

    def get_object(self, object_id: str) -> Optional[Recipe]:
        """
        Retrieves a single recipe object by ID.
        """
        with self.lock:
            item = self.objects.get(object_id)
            return item["recipe"] if item else None

    def delete_object(self, object_id: str) -> bool:
        """
        Deletes a recipe object from Weaviate by ID.
        """
        with self.lock:
            if object_id in self.objects:
                del self.objects[object_id]
                return True
            return False

    def list_objects(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        Lists stored recipe objects with pagination.
        """
        with self.lock:
            items = list(self.objects.values())[offset : offset + limit]
            return [item["recipe"] for item in items]

    def reset(self) -> None:
        """
        Purges all stored objects for test isolation.
        """
        with self.lock:
            self.objects.clear()

    def query_near_text(
        self,
        concepts: List[str],
        certainty: float = 0.50,
        limit: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[ScoredRecipeMatch]:
        """
        Executes Weaviate nearText semantic search using conceptual flavor descriptions.
        """
        combined_query = " ".join(concepts)
        query_vector = self.embedder.embed_text(combined_query)

        with self.lock:
            candidates: List[Tuple[float, float, Dict[str, Any]]] = []

            for oid, item in self.objects.items():
                props = item["properties"]

                # Apply Weaviate GraphQL where filter if specified
                if where and not self._evaluate_where(props, where):
                    continue

                dist, cert = self.embedder.compute_distance_and_certainty(
                    query_vector,
                    item["vector"],
                )

                if cert >= certainty:
                    candidates.append((cert, dist, item))

            # Rank descending by certainty
            candidates.sort(key=lambda x: x[0], reverse=True)
            top_matches = candidates[:limit]

            matches: List[ScoredRecipeMatch] = []
            for cert, dist, item in top_matches:
                matches.append(
                    ScoredRecipeMatch(
                        id=item["id"],
                        recipe=item["recipe"],
                        certainty=round(cert, 4),
                        distance=round(dist, 4),
                        score=round(cert, 4),
                    )
                )

            return matches

    def query_hybrid(
        self,
        query: str,
        alpha: float = 0.75,
        limit: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[ScoredRecipeMatch]:
        """
        Executes Weaviate hybrid search blending nearText semantic vectors with BM25 keyword matching.
        """
        query_vector = self.embedder.embed_text(query)
        q_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", query.lower()))

        with self.lock:
            candidates: List[Tuple[float, float, float, Dict[str, Any]]] = []

            for oid, item in self.objects.items():
                props = item["properties"]

                if where and not self._evaluate_where(props, where):
                    continue

                # 1. Vector certainty
                dist, cert = self.embedder.compute_distance_and_certainty(
                    query_vector,
                    item["vector"],
                )

                # 2. BM25 keyword score: text overlap on title, description, and ingredients
                doc_text = f"{props.get('title', '')} {props.get('description', '')} {' '.join(props.get('ingredients', []))}".lower()
                doc_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", doc_text))

                if q_tokens:
                    overlap = len(q_tokens.intersection(doc_tokens))
                    bm25_score = min(1.0, overlap / float(len(q_tokens)))
                else:
                    bm25_score = 0.0

                # 3. Hybrid blended score
                combined_score = (alpha * cert) + ((1.0 - alpha) * bm25_score)
                candidates.append((combined_score, cert, dist, item))

            candidates.sort(key=lambda x: x[0], reverse=True)
            top_matches = candidates[:limit]

            matches: List[ScoredRecipeMatch] = []
            for combined_score, cert, dist, item in top_matches:
                matches.append(
                    ScoredRecipeMatch(
                        id=item["id"],
                        recipe=item["recipe"],
                        certainty=round(cert, 4),
                        distance=round(dist, 4),
                        score=round(combined_score, 4),
                    )
                )

            return matches

    def _evaluate_where(self, props: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """
        Evaluates Weaviate GraphQL 'where' filter syntax against object properties.
        Supports: Equal, NotEqual, GreaterThan, LessThan, ContainsAny, And, Or.
        """
        # Handle compound operator: And
        if "operands" in where and where.get("operator") == "And":
            return all(self._evaluate_where(props, op) for op in where["operands"])

        # Handle compound operator: Or
        if "operands" in where and where.get("operator") == "Or":
            return any(self._evaluate_where(props, op) for op in where["operands"])

        path = where.get("path", [])
        if not path:
            return True

        field = path[0]
        actual_value = props.get(field)
        op = where.get("operator", "Equal")

        if op == "Equal":
            target = where.get("valueText") or where.get("valueInt") or where.get("valueNumber") or where.get("valueBoolean")
            if isinstance(actual_value, str) and isinstance(target, str):
                return actual_value.lower() == target.lower()
            return actual_value == target

        if op == "NotEqual":
            target = where.get("valueText") or where.get("valueInt")
            return actual_value != target

        if op in ("GreaterThan", "GreaterThanEqual"):
            target = where.get("valueInt") or where.get("valueNumber") or 0
            if actual_value is None:
                return False
            return actual_value >= target if op == "GreaterThanEqual" else actual_value > target

        if op in ("LessThan", "LessThanEqual"):
            target = where.get("valueInt") or where.get("valueNumber") or 999999
            if actual_value is None:
                return False
            return actual_value <= target if op == "LessThanEqual" else actual_value < target

        if op == "ContainsAny":
            # For array fields (e.g. dietary_tags, ingredients)
            single_val = where.get("valueText")
            target_list = where.get("valueTextArray") or ([single_val] if single_val else [])
            target_list_lower = [t.lower() for t in target_list]
            if isinstance(actual_value, list):
                actual_lower = [str(x).lower() for x in actual_value]
                return any(t in actual_lower for t in target_list_lower)
            elif isinstance(actual_value, str):
                return actual_value.lower() in target_list_lower
            return False

        if op == "ContainsAll":
            single_val = where.get("valueText")
            target_list = where.get("valueTextArray") or ([single_val] if single_val else [])
            target_list_lower = [t.lower() for t in target_list]
            if isinstance(actual_value, list):
                actual_lower = [str(x).lower() for x in actual_value]
                return all(t in actual_lower for t in target_list_lower)
            elif isinstance(actual_value, str):
                return actual_value.lower() in target_list_lower
            return False

        return True
