from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from analyzer import build_journey_insights

app = FastAPI(
    title="Journey Insights API",
    description="Takes a list of journey events and returns analytics (summary, steps, graph).",
    version="0.1.0",
)


class InsightsRequest(BaseModel):
    events: List[Dict[str, Any]]


@app.get("/")
def health() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


@app.post("/journey-insights")
def journey_insights(req: InsightsRequest) -> Dict[str, Any]:
    """
    Accepts a list of events, returns base analytics (no AI yet).
    """
    base = build_journey_insights(req.events)
    if base is None:
        raise HTTPException(status_code=400, detail="No events provided")

    return {"base": base}
