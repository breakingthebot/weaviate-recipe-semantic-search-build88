# Changelog

All notable changes to the **Build 88: Weaviate Recipe Semantic Search Engine** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-20

### Added
- **Weaviate Vector Engine Replica (`MemoryWeaviate`)**:
  - Full implementation of Weaviate `Recipe` class schema featuring properties for title, sensory description, ingredients, cuisine, dietary tags, cooking times, calories, and difficulty.
  - GraphQL-style nested `where` filter evaluator supporting `Equal`, `NotEqual`, `GreaterThan`, `LessThan`, `ContainsAny`, `ContainsAll`, `And`, and `Or`.
  - Object CRUD operations: `create_object`, `get_object`, `list_objects`, and `delete_object`.
- **Culinary Vector Embedder (`CulinaryEmbedder`)**:
  - Deterministic 128-dimensional dense vector generator with culinary flavor cluster expansions (`creamy`, `spicy`, `cozy`, `fresh`, `smoky`, `healthy`).
  - Character n-gram subword modeling for lexical stems and variations.
  - L2 unit-norm scaling and cosine distance/certainty calculation ($Certainty = 1.0 - Distance / 2.0$).
- **Weaviate Search Primitives**:
  - `nearText` sensory description retrieval matching dishes by abstract flavor cravings rather than rigid keywords.
  - Hybrid search blending dense vectors and BM25 sparse keyword matching with configurable $\alpha$ parameter.
- **Generative Chef & Sommelier Pipeline**:
  - Automatic recipe pairing based on natural language cravings and dietary restrictions.
  - Generates bespoke beverage pairing suggestions and smart dietary ingredient substitutions.
- **FastAPI REST API**:
  - `/api/recipes`: Recipe catalog listing, creation, retrieval, and deletion.
  - `/api/search/semantic`: Weaviate `nearText` query endpoint.
  - `/api/search/hybrid`: Weaviate hybrid BM25 and vector search endpoint.
  - `/api/recipes/recommend`: Sommelier and chef recommendation endpoint.
  - `/api/system/schema`: Class schema inspection and telemetry.
  - `/api/system/reset` & `/api/system/seed`: Deterministic state reset and catalog reseed harness.
- **Interactive Web Showcase Dashboard (`/dashboard`)**:
  - Dark glassmorphic culinary theme with tabbed layout.
  - Sensory `nearText` search with preset flavor idea pills and live certainty gauges.
  - Hybrid alpha slider with dynamic weight ratio visualization.
  - Chef recommendation card with sommelier pairings and substitution tips.
  - Live Weaviate schema property telemetry inspector.
- **Automated Test Suite**:
  - 36 automated unit and integration tests across embedder, memory Weaviate, recipe service, and FastAPI REST endpoints with 100% pass rate.
