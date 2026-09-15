from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_session
from ..services.usage import usage_stats

router = APIRouter(prefix="/api", tags=["usage"])


@router.get("/usage")
def usage(
    start: date | None = None,
    end: date | None = None,
    provider: str | None = None,
    model: str | None = None,
    feature: str | None = None,
    session: Session = Depends(get_session),
) -> dict:
    return usage_stats(
        session, start=start, end=end, provider=provider, model=model, feature=feature
    )
