"""
Build 88 — Weaviate Recipe Semantic Search Engine
Unit Tests for CulinaryEmbedder
"""

import math
import numpy as np
import pytest

from src.engine.embedder import CulinaryEmbedder, get_culinary_embedder
from src.config import settings


def test_embedder_dimension():
    """
    Verifies that the embedding dimension strictly matches config dimension.
    """
    embedder = get_culinary_embedder()
    text = "Crispy golden garlic roasted potatoes with fresh rosemary"
    vec = embedder.embed_text(text)
    assert len(vec) == settings.EMBEDDING_DIMENSION
    assert len(vec) == 128


def test_embedder_unit_norm():
    """
    Verifies that produced vectors are L2-normalized unit vectors.
    """
    embedder = get_culinary_embedder()
    text = "Fiery Mexican street tacos with cilantro and lime"
    vec = embedder.embed_text(text)
    norm = np.linalg.norm(np.array(vec))
    assert math.isclose(norm, 1.0, rel_tol=1e-5)


def test_embedder_deterministic():
    """
    Verifies that identical strings produce identical vectors.
    """
    embedder = get_culinary_embedder()
    text = "Silky French chocolate mousse with sea salt"
    vec1 = embedder.embed_text(text)
    vec2 = embedder.embed_text(text)
    assert vec1 == vec2


def test_cosine_similarity_identical():
    """
    Verifies that identical vectors have cosine similarity of 1.0 and distance of 0.0.
    """
    embedder = get_culinary_embedder()
    vec = embedder.embed_text("Authentic Thai green coconut curry")
    similarity = embedder.cosine_similarity(vec, vec)
    distance = embedder.vector_distance(vec, vec)
    certainty = embedder.distance_to_certainty(distance)

    assert math.isclose(similarity, 1.0, rel_tol=1e-5)
    assert math.isclose(distance, 0.0, abs_tol=1e-5)
    assert math.isclose(certainty, 1.0, abs_tol=1e-5)


def test_cosine_distance_and_certainty_relationship():
    """
    Verifies Weaviate standard formula: certainty = 1.0 - (distance / 2.0).
    """
    embedder = get_culinary_embedder()
    dist_samples = [0.0, 0.2, 0.5, 0.8, 1.0, 1.4, 2.0]
    for dist in dist_samples:
        calculated_certainty = embedder.distance_to_certainty(dist)
        expected_certainty = 1.0 - (dist / 2.0)
        assert math.isclose(calculated_certainty, expected_certainty, rel_tol=1e-5)


def test_culinary_semantic_clustering():
    """
    Verifies that culinary flavor expansions produce high similarity between
    conceptually related culinary descriptions.
    """
    embedder = get_culinary_embedder()
    warm_italian_craving = "cozy warm winter comfort pasta with garlic cream and parmesan"
    creamy_fettuccine_text = "rich garlic cream sauce fettuccine alfredo with aged cheese"
    chilled_citrus_salad = "crisp chilled watermelon mint salad with lime vinaigrette"

    v_craving = embedder.embed_text(warm_italian_craving)
    v_pasta = embedder.embed_text(creamy_fettuccine_text)
    v_salad = embedder.embed_text(chilled_citrus_salad)

    sim_pasta = embedder.cosine_similarity(v_craving, v_pasta)
    sim_salad = embedder.cosine_similarity(v_craving, v_salad)

    # The warm pasta description must score higher than the chilled salad
    assert sim_pasta > sim_salad


def test_embed_empty_text_returns_zero_vector():
    """
    Verifies that empty string or only stopwords returns all-zero vector.
    """
    embedder = get_culinary_embedder()
    vec = embedder.embed_text("")
    assert len(vec) == 128
    assert all(x == 0.0 for x in vec)


def test_flavor_clusters_expansion_coverage():
    """
    Verifies that all defined flavor clusters trigger expansions.
    """
    embedder = get_culinary_embedder()
    for cluster_name in embedder.flavor_clusters.keys():
        tokens = embedder._tokenize(cluster_name)
        assert f"__flavor_{cluster_name}__" in tokens
