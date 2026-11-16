"""Framework-agnostic HTTP router for the Python portfolio backend.

Used identically by both Vercel's Serverless Function handler (api/index.py)
and the local Python HTTP server (backend/local_server.py).
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from backend.analytics_engine import (
    analyze_project_architecture,
    analyze_repository_languages,
    build_full_portfolio_payload,
    compute_academic_analytics,
    filter_and_analyze_skills,
    lookup_knowledge_topic,
)
from backend.cgpa_projector import generate_academic_projection_report
from backend.contact_processor import get_contact_summary, process_contact_submission
from backend.trip_planner_service import evaluate_trip_plan, parse_trip_plan_payload

ResponseTuple = Tuple[int, Dict[str, str], Dict[str, Any]]


def _default_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def _first_param(query: Dict[str, List[str]], key: str, default: str = "") -> str:
    values = query.get(key)
    if not values:
        return default
    return values[0]


def _parse_json_body(body_bytes: bytes) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not body_bytes:
        return {}, None
    try:
        decoded = body_bytes.decode("utf-8")
        parsed = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "Request body must be valid UTF-8 JSON."

    if not isinstance(parsed, dict):
        return None, "JSON payload must be an object."
    return parsed, None


def dispatch_request(
    method: str,
    raw_url: str,
    body_bytes: bytes = b"",
) -> ResponseTuple:
    """Route an HTTP request to the corresponding Python data-processing service."""
    headers = _default_headers()
    upper_method = (method or "GET").upper()

    if upper_method == "OPTIONS":
        return 204, headers, {}

    parsed = urlparse(raw_url)
    path = parsed.path.rstrip("/") or "/"
    query = parse_qs(parsed.query)

    if path in ("/api/health", "/health"):
        lang_stats = analyze_repository_languages()
        return 200, headers, {
            "ok": True,
            "service": "sai-portfolio-python-backend",
            "python_version": sys.version.split()[0],
            "platform": platform.system(),
            "python_codebase_share": lang_stats.get("python_percentage", 0.0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    if path == "/api/portfolio" and upper_method == "GET":
        payload = build_full_portfolio_payload()
        return 200, headers, payload

    if path == "/api/analytics" and upper_method == "GET":
        academic = compute_academic_analytics()
        skills = filter_and_analyze_skills()
        languages = analyze_repository_languages()
        return 200, headers, {
            "academic": academic,
            "skills_summary": {
                "total_count": skills["total_count"],
                "average_proficiency": skills["average_proficiency"],
                "level_counts": skills["level_counts"],
                "category_breakdown": skills["category_breakdown"],
            },
            "codebase_languages": languages,
        }

    if path == "/api/analytics/projection" and upper_method == "GET":
        raw_sgpa = _first_param(query, "assumed_sgpa", "8.6")
        try:
            assumed_sgpa = float(raw_sgpa)
        except ValueError:
            return 400, headers, {"ok": False, "message": "assumed_sgpa must be a valid number."}
        report = generate_academic_projection_report(assumed_future_sgpa=assumed_sgpa)
        return 200, headers, report

    if path == "/api/skills" and upper_method == "GET":
        category = _first_param(query, "category", "all")
        search = _first_param(query, "q", "")
        sort_by = _first_param(query, "sort", "default")
        result = filter_and_analyze_skills(category=category, query=search, sort_by=sort_by)
        return 200, headers, result

    if path == "/api/knowledge" and upper_method == "GET":
        topic_id = _first_param(query, "topic", "")
        search = _first_param(query, "q", "")
        result = lookup_knowledge_topic(topic_id=topic_id or None, query=search)
        status = 200 if result.get("found") else 404
        return status, headers, result

    if path == "/api/projects" and upper_method == "GET":
        layer_id = _first_param(query, "layer", "")
        result = analyze_project_architecture(layer_id=layer_id or None)
        return 200, headers, result

    if path == "/api/trip-guide":
        if upper_method == "GET":
            return 200, headers, evaluate_trip_plan()
        if upper_method == "POST":
            body_json, error = _parse_json_body(body_bytes)
            if error or body_json is None:
                return 400, headers, {"ok": False, "message": error or "Invalid JSON."}
            plan, errors = parse_trip_plan_payload(body_json)
            if errors or plan is None:
                return 400, headers, {"ok": False, "errors": errors, "message": errors[0]}
            return 200, headers, evaluate_trip_plan(plan)
        return 405, headers, {"ok": False, "message": f"Method {upper_method} not allowed."}

    if path == "/api/contact":
        if upper_method == "GET":
            return 200, headers, get_contact_summary()
        if upper_method == "POST":
            body_json, error = _parse_json_body(body_bytes)
            if error or body_json is None:
                return 400, headers, {"ok": False, "message": error or "Invalid JSON."}
            status, result = process_contact_submission(body_json)
            return status, headers, result
        return 405, headers, {"ok": False, "message": f"Method {upper_method} not allowed."}

    return 404, headers, {
        "ok": False,
        "message": f"Unknown API endpoint: {path}",
        "available_endpoints": [
            "/api/health",
            "/api/portfolio",
            "/api/analytics",
            "/api/analytics/projection",
            "/api/skills",
            "/api/knowledge",
            "/api/projects",
            "/api/trip-guide",
            "/api/contact",
        ],
    }
