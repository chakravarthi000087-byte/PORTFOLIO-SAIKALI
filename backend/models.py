"""Typed data models and serialization helpers for the portfolio Python backend."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class QuickStat:
    """Represents a headline metric box rendered in the hero quick-stats row."""

    value: str
    label: str
    numeric_value: Optional[float] = None
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemesterMetric:
    """Represents academic performance for a single engineering semester."""

    semester: int
    label: str
    status: str
    sgpa: Optional[float]
    max_sgpa: float = 10.0
    progress_percent: float = 0.0
    credits: int = 20

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["display_score"] = (
            f"{self.sgpa:.2f} / {int(self.max_sgpa)}"
            if self.sgpa is not None
            else self.status
        )
        return payload


@dataclass(frozen=True)
class EducationProfile:
    """Represents university degree metadata and semester breakdown."""

    institution: str
    location: str
    degree: str
    period: str
    current_year_label: str
    focus: str
    current_semester: int
    total_semesters: int
    semesters: List[SemesterMetric] = field(default_factory=list)

    @property
    def degree_progress_percent(self) -> float:
        if self.total_semesters <= 0:
            return 0.0
        return round((self.current_semester / self.total_semesters) * 100.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "institution": self.institution,
            "location": self.location,
            "degree": self.degree,
            "period": self.period,
            "current_year_label": self.current_year_label,
            "focus": self.focus,
            "current_semester": self.current_semester,
            "total_semesters": self.total_semesters,
            "degree_progress_percent": self.degree_progress_percent,
            "semesters": [sem.to_dict() for sem in self.semesters],
        }


@dataclass(frozen=True)
class SkillItem:
    """Represents a technical skill with category, proficiency level, and percentage."""

    id: str
    name: str
    category: str  # "languages" | "web" | "tools"
    category_label: str
    level: str  # "Beginner" | "Intermediate" | "Advanced"
    proficiency: int  # 0..100
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoreKnowledgeTopic:
    """Represents an interactive Computer Science foundational topic."""

    id: str
    title: str
    short_label: str
    description: str
    applied_in: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureLayer:
    """Represents a single layer tab inside the Trip Guide Architecture Explorer."""

    id: str
    tab_label: str
    title: str
    summary: str
    highlights: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectShowcase:
    """Represents the featured project specification and architecture breakdown."""

    id: str
    title: str
    stage_label: str
    description: str
    tech_tags: List[str]
    live_url: str
    github_url: str
    layers: List[ArchitectureLayer] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "stage_label": self.stage_label,
            "description": self.description,
            "tech_tags": list(self.tech_tags),
            "live_url": self.live_url,
            "github_url": self.github_url,
            "layers": [layer.to_dict() for layer in self.layers],
        }


@dataclass(frozen=True)
class AchievementCard:
    """Represents an achievement or profile summary card."""

    id: str
    icon: str
    title: str
    description: str
    chips: List[str] = field(default_factory=list)
    highlight_first_chip: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContactChannel:
    """Represents a direct contact channel with optional copy or external link action."""

    id: str
    label: str
    display_value: str
    action_type: str  # "copy" | "link"
    action_value: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContactSubmission:
    """Validated and sanitized contact form submission stored by the Python backend."""

    submission_id: str
    sender_name: str
    sender_email: str
    message: str
    submitted_at: str
    fingerprint: str
    mailto_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HeroProfile:
    """Represents the primary portfolio owner identity and hero metadata."""

    brand_initials: str
    brand_name: str
    full_name: str
    initials_fallback: str
    status_badge: str
    summary: str
    roles: List[str]
    location: str
    university_short: str
    hackathon_badge: str
    batch_period: str
    github_url: str
    linkedin_url: str
    float_chip_title: str
    float_chip_subtitle: str
    quick_stats: List[QuickStat] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brand_initials": self.brand_initials,
            "brand_name": self.brand_name,
            "full_name": self.full_name,
            "initials_fallback": self.initials_fallback,
            "status_badge": self.status_badge,
            "summary": self.summary,
            "roles": list(self.roles),
            "location": self.location,
            "university_short": self.university_short,
            "hackathon_badge": self.hackathon_badge,
            "batch_period": self.batch_period,
            "github_url": self.github_url,
            "linkedin_url": self.linkedin_url,
            "float_chip_title": self.float_chip_title,
            "float_chip_subtitle": self.float_chip_subtitle,
            "quick_stats": [stat.to_dict() for stat in self.quick_stats],
        }
