"""
Culinary Vector Embedder Engine for Weaviate Recipe Search.
Encodes recipe descriptions, taste profiles, textures, and ingredients
into normalized 128-dimensional dense float vectors.
"""

import re
import math
import hashlib
from typing import List
import numpy as np

from src.config import settings


class CulinaryEmbedder:
    """
    Computes unit-normalized dense float vectors optimized for culinary concepts,
    sensory flavor profiles, cooking techniques, and dietary tags.
    """

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension
        self.stopwords = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "down", "is", "are", "was", "were",
            "this", "that", "it", "its", "as", "be", "been", "being", "have", "has",
            "you", "your", "can", "will", "our", "their", "just", "very", "also"
        }

        # Semantic culinary synonym clusters that boost cross-term similarity
        self.flavor_clusters = {
            "creamy": ["velvety", "rich", "indulgent", "buttery", "silky", "cheese", "cream", "parmesan", "sauce"],
            "spicy": ["hot", "fiery", "chili", "peppery", "zesty", "kick", "jalapeno", "sriracha", "tangy"],
            "cozy": ["comforting", "warm", "hearty", "homestyle", "rustic", "autumn", "winter", "rainy", "trattoria"],
            "fresh": ["crisp", "bright", "herby", "herbaceous", "citrus", "lemon", "lime", "basil", "mint", "summer"],
            "smoky": ["charred", "barbecue", "bbq", "roasted", "grilled", "woodsmoke", "chipotle"],
            "healthy": ["light", "nutritious", "clean", "wholesome", "keto", "low-carb", "gluten-free", "vegan"],
        }

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text into cleaned lowercase terms, applies culinary cluster expansion,
        and generates character tri-grams.
        """
        cleaned = text.lower()
        raw_words = re.findall(r"\b[a-zA-Z0-9_-]+\b", cleaned)
        base_words = [w for w in raw_words if len(w) >= 2 and w not in self.stopwords]

        expanded_tokens: List[str] = list(base_words)

        # Flavor cluster expansion: if a word appears in a cluster, add cluster seeds
        for word in base_words:
            for cluster_key, cluster_terms in self.flavor_clusters.items():
                if word == cluster_key or word in cluster_terms:
                    expanded_tokens.append(f"__flavor_{cluster_key}__")

        # Add character tri-grams for subword matching (handles stems, variations)
        for word in base_words:
            if len(word) >= 4:
                for i in range(len(word) - 2):
                    expanded_tokens.append(word[i : i + 3])

        return expanded_tokens

    def embed_text(self, text: str) -> List[float]:
        """
        Transforms culinary text or flavor query into an L2-normalized dense vector.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        tokens = self._tokenize(text)

        if not tokens:
            return vec.tolist()

        counts: dict[str, float] = {}
        for token in tokens:
            weight = 3.0 if token.startswith("__flavor_") else 1.0
            counts[token] = counts.get(token, 0.0) + weight

        for token, count in counts.items():
            # Hash to bucket coordinate in [0, dimension - 1]
            bucket_idx = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dimension
            # Signed feature projection
            sign = 1.0 if (int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:4], 16) % 2 == 0) else -1.0
            term_weight = (1.0 + math.log(max(1.0, count))) * sign
            vec[bucket_idx] += term_weight

        # L2 unit normalization
        norm = float(np.linalg.norm(vec))
        if norm > 1e-6:
            vec = vec / norm

        return [float(x) for x in vec]

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Computes cosine similarity between two float vectors.
        """
        u = np.array(vec_a, dtype=np.float32)
        v = np.array(vec_b, dtype=np.float32)
        dot = float(np.dot(u, v))
        return float(max(-1.0, min(1.0, dot)))

    def vector_distance(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Computes cosine distance (1.0 - cosine_similarity).
        """
        sim = self.cosine_similarity(vec_a, vec_b)
        return float(max(0.0, 1.0 - sim))

    def distance_to_certainty(self, distance: float) -> float:
        """
        Converts Weaviate cosine distance to certainty score: 1.0 - (distance / 2.0).
        """
        return float(max(0.0, min(1.0, 1.0 - (distance / 2.0))))

    def compute_distance_and_certainty(self, vec_a: List[float], vec_b: List[float]) -> tuple[float, float]:
        """
        Calculates cosine distance and Weaviate certainty score.
        Weaviate Certainty = 1.0 - (Distance / 2.0)
        """
        dist = self.vector_distance(vec_a, vec_b)
        cert = self.distance_to_certainty(dist)
        return dist, cert


_culinary_embedder_instance = CulinaryEmbedder(dimension=settings.VECTOR_DIMENSION)


def get_culinary_embedder() -> CulinaryEmbedder:
    """
    Returns the singleton culinary vector embedder.
    """
    global _culinary_embedder_instance
    return _culinary_embedder_instance
