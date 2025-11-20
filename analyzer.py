from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def parse_time(t: str) -> datetime:
    """
    Parse an ISO-like timestamp string into a datetime.
    Assumes Z or offset; replaces 'Z' with '+00:00' if present.
    """
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


def classify_stage(event: Dict[str, Any]) -> str:
    """
    Map an event into a coarse-grained journey stage based on title/tags.
    This is intentionally simple and can be refined later.
    """
    ui = event.get("uiData", {}) or {}
    title = (ui.get("title") or "").lower()
    tags = [str(t).lower() for t in ui.get("filterTags", [])]

    if "payment" in title or "payments" in tags:
        return "Payment"
    if "whatsapp" in title or "whatsapp" in tags:
        return "WhatsApp"
    if "otp auth" in title or "otp" in tags:
        return "Auth"
    if "delivery" in title or "issue" in tags:
        return "Issue"
    if "booking" in title or "appointment" in tags:
        return "Booking"
    return "Other"


def build_journey_insights(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Core analytics:
    - Sort events by time
    - Build 'steps' list (chronological)
    - Build 'summary' (total interactions, channels, first/last contact)
    - Build 'graph' (nodes=stages, edges=transitions between stages)
    Returns None if no events are provided.
    """
    if not events:
        return None

    # Sort chronologically
    events_sorted = sorted(events, key=lambda e: parse_time(e["time"]))

    steps: List[Dict[str, Any]] = []
    channels = set()
    edges: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
        lambda: {"count": 0, "total_delta_minutes": 0.0}
    )

    prev_stage: Optional[str] = None
    prev_time: Optional[datetime] = None

    for e in events_sorted:
        ui = e.get("uiData", {}) or {}
        data = e.get("data", {}) or {}

        event_time = parse_time(e["time"])
        stage = classify_stage(e)

        channel = (
            data.get("📱 Channel")
            or data.get("🛒 Channel")
            or data.get("🧭 Channel")
            or "Unknown"
        )
        channels.add(channel)

        step = {
            "id": e.get("id", e["time"]),
            "label": ui.get("title", "Event"),
            "subtitle": ui.get("subTitle"),
            "channel": channel,
            "time": event_time.isoformat(),
            "category": stage,
            "sentiment": data.get("🧠 Sentiment"),
        }
        steps.append(step)

        if prev_stage is not None and prev_time is not None:
            delta_minutes = (event_time - prev_time).total_seconds() / 60.0
            key = (prev_stage, stage)
            edges[key]["count"] += 1
            # Avoid negative deltas in case of out-of-order data
            edges[key]["total_delta_minutes"] += max(delta_minutes, 0)

        prev_stage = stage
        prev_time = event_time

    first_time = parse_time(steps[0]["time"])
    last_time = parse_time(steps[-1]["time"])

    summary = {
        "totalInteractions": len(steps),
        "channelsUsed": sorted(channels),
        "firstContact": first_time.isoformat(),
        "lastContact": last_time.isoformat(),
    }

    stage_counts = Counter(step["category"] for step in steps)
    nodes = [
        {"id": stage, "label": stage, "count": count}
        for stage, count in stage_counts.items()
    ]

    graph_edges: List[Dict[str, Any]] = []
    for (from_stage, to_stage), info in edges.items():
        avg_minutes = (
            info["total_delta_minutes"] / info["count"] if info["count"] else None
        )
        graph_edges.append(
            {
                "from": from_stage,
                "to": to_stage,
                "count": info["count"],
                "avgMinutes": avg_minutes,
            }
        )

    return {
        "summary": summary,
        "steps": steps,
        "graph": {
            "nodes": nodes,
            "edges": graph_edges,
        },
    }
