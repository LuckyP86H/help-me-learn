"""Every LLM call flows through run_chat so nothing escapes the usage log."""

import time
from dataclasses import dataclass
from datetime import date, datetime, time as dtime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import UsageLog
from ..providers.base import ChatResult
from ..providers.registry import get_provider


@dataclass
class LoggedChat:
    result: ChatResult
    provider: str
    latency_ms: int


def run_chat(
    session: Session,
    provider_name: str,
    messages: list[dict],
    model: str | None = None,
    feature: str = "chat",
) -> LoggedChat:
    provider = get_provider(provider_name)
    start = time.perf_counter()
    result = provider.chat(messages, model)
    latency_ms = int((time.perf_counter() - start) * 1000)
    log_usage(
        session,
        provider=provider.name,
        model=result.model,
        feature=feature,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=latency_ms,
    )
    return LoggedChat(result=result, provider=provider.name, latency_ms=latency_ms)


def log_usage(
    session: Session,
    provider: str,
    model: str,
    feature: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
) -> None:
    session.add(
        UsageLog(
            provider=provider,
            model=model,
            feature=feature,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
    )
    session.commit()


def usage_stats(
    session: Session,
    start: date | None = None,
    end: date | None = None,
    provider: str | None = None,
    model: str | None = None,
    feature: str | None = None,
) -> dict:
    """Aggregate the usage log for the dashboard, honoring the given filters."""
    conditions = []
    if start:
        conditions.append(UsageLog.ts >= datetime.combine(start, dtime.min, timezone.utc))
    if end:
        conditions.append(UsageLog.ts <= datetime.combine(end, dtime.max, timezone.utc))
    if provider:
        conditions.append(UsageLog.provider == provider)
    if model:
        conditions.append(UsageLog.model == model)
    if feature:
        conditions.append(UsageLog.feature == feature)

    def grouped(*columns):
        stmt = (
            select(
                *columns,
                func.count(UsageLog.id).label("calls"),
                func.sum(UsageLog.input_tokens).label("input_tokens"),
                func.sum(UsageLog.output_tokens).label("output_tokens"),
                func.avg(UsageLog.latency_ms).label("avg_latency_ms"),
            )
            .where(*conditions)
            .group_by(*columns)
        )
        return session.execute(stmt).all()

    day = func.date(UsageLog.ts).label("day")
    daily = [
        {
            "date": row.day,
            "calls": row.calls,
            "input_tokens": row.input_tokens or 0,
            "output_tokens": row.output_tokens or 0,
        }
        for row in sorted(grouped(day), key=lambda r: r.day)
    ]
    by_provider = [
        {
            "provider": row.provider,
            "calls": row.calls,
            "input_tokens": row.input_tokens or 0,
            "output_tokens": row.output_tokens or 0,
            "avg_latency_ms": round(row.avg_latency_ms or 0),
        }
        for row in grouped(UsageLog.provider)
    ]
    by_model = [
        {
            "provider": row.provider,
            "model": row.model,
            "calls": row.calls,
            "input_tokens": row.input_tokens or 0,
            "output_tokens": row.output_tokens or 0,
        }
        for row in grouped(UsageLog.provider, UsageLog.model)
    ]
    by_feature = [
        {
            "feature": row.feature,
            "calls": row.calls,
            "input_tokens": row.input_tokens or 0,
            "output_tokens": row.output_tokens or 0,
        }
        for row in grouped(UsageLog.feature)
    ]
    totals = {
        "calls": sum(d["calls"] for d in daily),
        "input_tokens": sum(d["input_tokens"] for d in daily),
        "output_tokens": sum(d["output_tokens"] for d in daily),
    }
    return {
        "daily": daily,
        "by_provider": by_provider,
        "by_model": by_model,
        "by_feature": by_feature,
        "totals": totals,
    }
