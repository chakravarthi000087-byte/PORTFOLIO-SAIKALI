"""Python data processing and analytics engine for the portfolio backend.

Performs academic CGPA computations, skill proficiency aggregations,
query filtering/ranking, core knowledge indexing, and source-tree language
distribution analysis.
"""

from __future__ import annotations

import os
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.models import CoreKnowledgeTopic, EducationProfile, SkillItem
from backend.portfolio_data import (
    get_achievement_cards,
    get_contact_channels,
    get_core_knowledge_topics,
    get_education_profile,
    get_featured_project,
    get_hero_profile,
    get_skills_catalog,
)

EXCLUDED_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".vercel",
    "coverage",
}

LANGUAGE_EXTENSION_MAP = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".css": "CSS",
    ".html": "HTML",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
}


def compute_academic_analytics(education: Optional[EducationProfile] = None) -> Dict[str, Any]:
    """Compute weighted CGPA, SGPA statistics, and degree progression metrics."""
    edu = education or get_education_profile()
    completed = [sem for sem in edu.semesters if sem.sgpa is not None]

    if not completed:
        return {
            "completed_semesters": 0,
            "total_credits_completed": 0,
            "cumulative_cgpa": 0.0,
            "mean_sgpa": 0.0,
            "sgpa_stdev": 0.0,
            "highest_sgpa": 0.0,
            "lowest_sgpa": 0.0,
            "latest_delta": 0.0,
            "degree_progress_percent": edu.degree_progress_percent,
            "standing": "In Progress",
        }

    sgpas = [float(sem.sgpa) for sem in completed if sem.sgpa is not None]
    total_credits = sum(sem.credits for sem in completed)
    weighted_points = sum(float(sem.sgpa) * sem.credits for sem in completed if sem.sgpa is not None)
    weighted_cgpa = round(weighted_points / total_credits, 2) if total_credits > 0 else 0.0
    mean_sgpa = round(statistics.mean(sgpas), 2)
    stdev_sgpa = round(statistics.pstdev(sgpas), 3) if len(sgpas) > 1 else 0.0
    latest_delta = round(sgpas[-1] - sgpas[-2], 2) if len(sgpas) >= 2 else 0.0

    if weighted_cgpa >= 8.5:
        standing = "First Class with Distinction"
    elif weighted_cgpa >= 7.5:
        standing = "First Class"
    else:
        standing = "Good Standing"

    return {
        "completed_semesters": len(completed),
        "total_credits_completed": total_credits,
        "cumulative_cgpa": weighted_cgpa,
        "mean_sgpa": mean_sgpa,
        "sgpa_stdev": stdev_sgpa,
        "highest_sgpa": max(sgpas),
        "lowest_sgpa": min(sgpas),
        "latest_delta": latest_delta,
        "degree_progress_percent": edu.degree_progress_percent,
        "standing": standing,
    }


def filter_and_analyze_skills(
    category: str = "all",
    query: str = "",
    sort_by: str = "default",
    skills: Optional[List[SkillItem]] = None,
) -> Dict[str, Any]:
    """Filter, search, sort, and summarize technical skills on the Python backend."""
    catalog = skills or get_skills_catalog()
    normalized_cat = (category or "all").strip().lower()
    normalized_query = (query or "").strip().lower()
    normalized_sort = (sort_by or "default").strip().lower()

    filtered: List[SkillItem] = []
    for item in catalog:
        if normalized_cat not in ("", "all") and item.category.lower() != normalized_cat:
            continue
        if normalized_query:
            haystack = " ".join(
                [item.name, item.category_label, item.level, *item.keywords]
            ).lower()
            if normalized_query not in haystack:
                continue
        filtered.append(item)

    if normalized_sort == "proficiency":
        filtered.sort(key=lambda s: (-s.proficiency, s.name.lower()))
    elif normalized_sort == "name":
        filtered.sort(key=lambda s: s.name.lower())

    category_breakdown: Dict[str, Dict[str, Any]] = {}
    for item in catalog:
        bucket = category_breakdown.setdefault(
            item.category,
            {"count": 0, "total_proficiency": 0, "skills": []},
        )
        bucket["count"] += 1
        bucket["total_proficiency"] += item.proficiency
        bucket["skills"].append(item.name)

    for bucket in category_breakdown.values():
        bucket["average_proficiency"] = round(bucket["total_proficiency"] / bucket["count"], 1)
        del bucket["total_proficiency"]

    proficiencies = [s.proficiency for s in filtered]
    avg_proficiency = round(statistics.mean(proficiencies), 1) if proficiencies else 0.0
    level_counts = {
        "Beginner": sum(1 for s in filtered if s.level == "Beginner"),
        "Intermediate": sum(1 for s in filtered if s.level == "Intermediate"),
        "Advanced": sum(1 for s in filtered if s.level == "Advanced"),
    }

    return {
        "filter": normalized_cat,
        "query": normalized_query,
        "sort_by": normalized_sort,
        "total_count": len(catalog),
        "matched_count": len(filtered),
        "average_proficiency": avg_proficiency,
        "level_counts": level_counts,
        "category_breakdown": category_breakdown,
        "items": [item.to_dict() for item in filtered],
    }


def lookup_knowledge_topic(
    topic_id: Optional[str] = None,
    query: str = "",
) -> Dict[str, Any]:
    """Retrieve and search core CS knowledge modules."""
    topics: List[CoreKnowledgeTopic] = get_core_knowledge_topics()
    normalized_id = (topic_id or "").strip().lower()
    normalized_query = (query or "").strip().lower()

    if normalized_id:
        selected = next((t for t in topics if t.id == normalized_id), None)
        return {
            "found": selected is not None,
            "selected": selected.to_dict() if selected else None,
            "topics": [t.to_dict() for t in topics],
        }

    if normalized_query:
        matches = [
            t
            for t in topics
            if normalized_query in t.title.lower()
            or normalized_query in t.description.lower()
            or any(normalized_query in app.lower() for app in t.applied_in)
        ]
        return {
            "found": len(matches) > 0,
            "query": normalized_query,
            "matched_count": len(matches),
            "topics": [t.to_dict() for t in matches],
        }

    return {
        "found": True,
        "selected": topics[0].to_dict() if topics else None,
        "topics": [t.to_dict() for t in topics],
    }


def analyze_project_architecture(layer_id: Optional[str] = None) -> Dict[str, Any]:
    """Process and return Trip Guide architecture layer details and component counts."""
    project = get_featured_project()
    layers = project.layers
    normalized_layer = (layer_id or "").strip().lower()

    selected_layer = None
    if normalized_layer:
        selected_layer = next((layer for layer in layers if layer.id == normalized_layer), None)

    unique_technologies = sorted(
        {tech for layer in layers for tech in layer.technologies}
    )

    return {
        "project": project.to_dict(),
        "selected_layer": selected_layer.to_dict() if selected_layer else None,
        "layer_count": len(layers),
        "unique_technologies": unique_technologies,
    }


def analyze_repository_languages(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Scan project source files to calculate byte counts and language percentages.

    Mirrors GitHub Linguist conventions by excluding build outputs, dependencies,
    and binary assets.
    """
    base_path = root_dir or Path(__file__).resolve().parent.parent
    bytes_by_language: Dict[str, int] = {}
    files_by_language: Dict[str, int] = {}

    if not base_path.exists():
        return {"total_bytes": 0, "languages": []}

    for current_root, dir_names, file_names in os.walk(base_path):
        dir_names[:] = [d for d in dir_names if d not in EXCLUDED_DIRS]
        for file_name in file_names:
            file_path = Path(current_root) / file_name
            lang = LANGUAGE_EXTENSION_MAP.get(file_path.suffix.lower())
            if not lang:
                continue
            try:
                size = file_path.stat().st_size
            except OSError:
                continue
            bytes_by_language[lang] = bytes_by_language.get(lang, 0) + size
            files_by_language[lang] = files_by_language.get(lang, 0) + 1

    total_bytes = sum(bytes_by_language.values())
    ranked = sorted(bytes_by_language.items(), key=lambda pair: -pair[1])

    languages = [
        {
            "language": lang,
            "bytes": byte_count,
            "files": files_by_language.get(lang, 0),
            "percentage": round((byte_count / total_bytes) * 100.0, 2) if total_bytes > 0 else 0.0,
        }
        for lang, byte_count in ranked
    ]

    python_share = next(
        (entry["percentage"] for entry in languages if entry["language"] == "Python"),
        0.0,
    )

    return {
        "total_bytes": total_bytes,
        "python_percentage": python_share,
        "languages": languages,
    }


def build_full_portfolio_payload(root_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Assemble the complete hydrated portfolio payload from Python domain services."""
    base_path = root_dir or Path(__file__).resolve().parent.parent
    has_profile_photo = (base_path / "public" / "profile.jpg").is_file()

    hero = get_hero_profile()
    education = get_education_profile()
    skills_summary = filter_and_analyze_skills()
    knowledge_topics = get_core_knowledge_topics()
    project = get_featured_project()
    achievements = get_achievement_cards()
    contact_channels = get_contact_channels()
    academic_analytics = compute_academic_analytics(education)

    return {
        "hero": hero.to_dict(),
        "has_profile_photo": has_profile_photo,
        "profile_photo_url": "/profile.jpg" if has_profile_photo else None,
        "education": education.to_dict(),
        "academic_analytics": academic_analytics,
        "skills": skills_summary,
        "core_knowledge": [topic.to_dict() for topic in knowledge_topics],
        "featured_project": project.to_dict(),
        "achievements": [card.to_dict() for card in achievements],
        "contact_channels": [channel.to_dict() for channel in contact_channels],
    }
