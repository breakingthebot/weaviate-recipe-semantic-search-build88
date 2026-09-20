"""
FastAPI Application Entrypoint for Build 88: Weaviate Recipe Semantic Search Engine.
Demonstrates Weaviate class schemas, nearText sensory description search,
hybrid alpha blending, and generative chef recommendations.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.engine.weaviate_client import get_weaviate_engine
from src.services.recipe_service import get_recipe_service
from src.api.routes_recipes import router as recipes_router
from src.api.routes_search import router as search_router
from src.api.routes_system import router as system_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup and shutdown hooks.
    """
    get_weaviate_engine()
    # Initialize recipe service and seed dataset
    get_recipe_service()
    yield


app = FastAPI(
    title="Build 88: Weaviate Recipe Semantic Search Engine",
    description="Vector database semantic search powered by Weaviate nearText concepts, hybrid BM25 blending, and culinary sensory embeddings.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST sub-routers
app.include_router(recipes_router)
app.include_router(search_router)
app.include_router(system_router)

# Mount Static Dashboard Assets
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/dashboard", tags=["Showcase UI"])
def get_dashboard() -> FileResponse:
    """
    Serves the interactive Weaviate Recipe Search Engine Web Showcase Dashboard.
    """
    index_html = static_dir / "index.html"
    return FileResponse(index_html)


@app.get("/", tags=["Discovery"])
def root_discovery() -> Dict[str, Any]:
    """
    Root discovery endpoint providing architecture details, Weaviate class schema, and search guide.
    """
    engine = get_weaviate_engine()
    schema_info = engine.get_class_schema()

    return {
        "build": 88,
        "service": "Build 88: Weaviate Recipe Semantic Search Engine",
        "technology": "Weaviate Vector Database & FastAPI",
        "category": "Databases - Vector/Search",
        "version": "1.0.0",
        "weaviate_configuration": {
            "class_name": settings.WEAVIATE_CLASS_NAME,
            "vector_index_type": "hnsw",
            "distance_metric": "cosine",
            "vector_dimension": settings.VECTOR_DIMENSION,
            "total_objects": schema_info.total_objects,
        },
        "search_capabilities": {
            "near_text": "Semantic search by sensory descriptions, flavor profiles, and textures",
            "hybrid": "Blended search combining nearText vectors and BM25 keywords with alpha weighting",
            "where_filters": "GraphQL-style filtering on cuisine, prep_time_minutes, dietary_tags, and calories",
            "generative_chef": "Personalized pairing suggestions and ingredient substitution tips",
        },
        "endpoints": {
            "web_dashboard": "/dashboard",
            "list_recipes": "/api/recipes",
            "create_recipe": "/api/recipes",
            "near_text_search": "/api/search/semantic",
            "hybrid_search": "/api/search/hybrid",
            "chef_recommendation": "/api/recipes/recommend",
            "class_schema": "/api/system/schema",
        },
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
