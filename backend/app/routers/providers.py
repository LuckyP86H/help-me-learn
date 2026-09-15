from fastapi import APIRouter

from ..providers.registry import get_embedder, list_provider_info

router = APIRouter(prefix="/api", tags=["providers"])


@router.get("/providers")
def providers() -> dict:
    return {
        "providers": list_provider_info(),
        "embedding_provider": get_embedder().name,
    }
