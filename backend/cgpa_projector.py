"""Academic CGPA projection and target-planning engine for B.Tech CSE coursework.

Provides credit-weighted GPA calculations, remaining-semester target solvers,
variance/trend diagnostics, and structured academic progress reports for
A. Sai Kali Chakravarthi's 8-semester engineering degree track.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from backend.models import EducationProfile, SemesterMetric
from backend.portfolio_data import get_education_profile

DEFAULT_REMAINING_CREDITS_BY_SEMESTER: Dict[int, int] = {
    3: 22,
    4: 22,
    5: 22,
    6: 22,
    7: 18,
    8: 14,
}


@dataclass(frozen=True)
class TargetScenario:
    """Represents the SGPA required across remaining semesters to reach a target CGPA."""

    target_cgpa: float
    required_avg_sgpa: float
    achievable: bool
    difficulty: str
    margin_from_current: float
    remaining_credits: int
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemesterForecast:
    """Projected cumulative CGPA trajectory if a steady SGPA is maintained."""

    semester: int
    credits: int
    assumed_sgpa: float
    projected_cumulative_cgpa: float
    completion_percent: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_credit_weighted_cgpa(semesters: List[SemesterMetric]) -> float:
    """Compute exact credit-weighted CGPA across completed semesters."""
    total_points = 0.0
    total_credits = 0
    for sem in semesters:
        if sem.sgpa is not None and sem.credits > 0:
            total_points += float(sem.sgpa) * sem.credits
            total_credits += sem.credits
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 3)


def classify_difficulty(required_sgpa: float, baseline_sgpa: float) -> str:
    """Classify the effort level needed to achieve a target remaining SGPA."""
    if required_sgpa > 10.0:
        return "unreachable"
    delta = required_sgpa - baseline_sgpa
    if delta <= 0.0:
        return "comfortable"
    if delta <= 0.45:
        return "achievable"
    if delta <= 0.9:
        return "ambitious"
    return "stretch"


def compute_remaining_credits(education: EducationProfile) -> int:
    """Calculate total remaining credits across uncompleted semesters."""
    completed_nums = {sem.semester for sem in education.semesters if sem.sgpa is not None}
    remaining = 0
    for sem_num in range(1, education.total_semesters + 1):
        if sem_num in completed_nums:
            continue
        existing = next((s for s in education.semesters if s.semester == sem_num), None)
        if existing is not None:
            remaining += existing.credits
        else:
            remaining += DEFAULT_REMAINING_CREDITS_BY_SEMESTER.get(sem_num, 20)
    return remaining


def solve_target_cgpa_scenarios(
    targets: Optional[List[float]] = None,
    education: Optional[EducationProfile] = None,
) -> List[TargetScenario]:
    """Solve the average SGPA needed across remaining credits for target CGPAs."""
    edu = education or get_education_profile()
    desired_targets = targets or [8.5, 8.75, 9.0, 9.25]

    completed = [s for s in edu.semesters if s.sgpa is not None]
    completed_credits = sum(s.credits for s in completed)
    completed_points = sum(float(s.sgpa) * s.credits for s in completed if s.sgpa is not None)
    current_cgpa = calculate_credit_weighted_cgpa(edu.semesters)
    remaining_credits = compute_remaining_credits(edu)
    total_degree_credits = completed_credits + remaining_credits

    scenarios: List[TargetScenario] = []
    for target in desired_targets:
        bounded_target = max(0.0, min(10.0, float(target)))
        if remaining_credits <= 0:
            req_sgpa = current_cgpa
        else:
            required_total_points = bounded_target * total_degree_credits
            needed_remaining_points = required_total_points - completed_points
            req_sgpa = round(needed_remaining_points / remaining_credits, 2)

        achievable = 0.0 <= req_sgpa <= 10.0
        difficulty = classify_difficulty(req_sgpa, current_cgpa)
        margin = round(bounded_target - current_cgpa, 2)

        if not achievable:
            note = f"Requires {req_sgpa:.2f} SGPA (> 10.00 scale maximum)."
        elif difficulty == "comfortable":
            note = f"Maintain {req_sgpa:.2f} SGPA across remaining {remaining_credits} credits."
        else:
            note = (
                f"Requires {req_sgpa:.2f} average SGPA across remaining "
                f"{remaining_credits} credits (+{max(0.0, req_sgpa - current_cgpa):.2f} above current CGPA)."
            )

        scenarios.append(
            TargetScenario(
                target_cgpa=round(bounded_target, 2),
                required_avg_sgpa=req_sgpa,
                achievable=achievable,
                difficulty=difficulty,
                margin_from_current=margin,
                remaining_credits=remaining_credits,
                notes=note,
            )
        )

    return scenarios


def build_graduation_trajectory(
    assumed_future_sgpa: float = 8.6,
    education: Optional[EducationProfile] = None,
) -> List[SemesterForecast]:
    """Simulate semester-by-semester cumulative CGPA through graduation."""
    edu = education or get_education_profile()
    clamped_sgpa = max(0.0, min(10.0, float(assumed_future_sgpa)))

    running_points = 0.0
    running_credits = 0
    forecast: List[SemesterForecast] = []

    for sem_num in range(1, edu.total_semesters + 1):
        existing = next((s for s in edu.semesters if s.semester == sem_num), None)
        if existing is not None and existing.sgpa is not None:
            credits = existing.credits
            sgpa = float(existing.sgpa)
        elif existing is not None:
            credits = existing.credits
            sgpa = clamped_sgpa
        else:
            credits = DEFAULT_REMAINING_CREDITS_BY_SEMESTER.get(sem_num, 20)
            sgpa = clamped_sgpa

        running_points += sgpa * credits
        running_credits += credits
        cumulative = round(running_points / running_credits, 2) if running_credits > 0 else 0.0
        completion = round((sem_num / edu.total_semesters) * 100.0, 1)

        forecast.append(
            SemesterForecast(
                semester=sem_num,
                credits=credits,
                assumed_sgpa=round(sgpa, 2),
                projected_cumulative_cgpa=cumulative,
                completion_percent=completion,
            )
        )

    return forecast


def generate_academic_projection_report(
    assumed_future_sgpa: float = 8.6,
    targets: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Produce a comprehensive academic projection report for API consumers."""
    education = get_education_profile()
    completed = [s for s in education.semesters if s.sgpa is not None]
    sgpas = [float(s.sgpa) for s in completed if s.sgpa is not None]

    current_cgpa = calculate_credit_weighted_cgpa(education.semesters)
    completed_credits = sum(s.credits for s in completed)
    remaining_credits = compute_remaining_credits(education)
    total_credits = completed_credits + remaining_credits
    variance = round(statistics.pvariance(sgpas), 4) if len(sgpas) > 1 else 0.0
    std_dev = round(math.sqrt(variance), 4)

    scenarios = solve_target_cgpa_scenarios(targets=targets, education=education)
    trajectory = build_graduation_trajectory(
        assumed_future_sgpa=assumed_future_sgpa,
        education=education,
    )

    return {
        "institution": education.institution,
        "degree": education.degree,
        "current_semester": education.current_semester,
        "total_semesters": education.total_semesters,
        "completed_credits": completed_credits,
        "remaining_credits": remaining_credits,
        "total_degree_credits": total_credits,
        "current_weighted_cgpa": current_cgpa,
        "sgpa_variance": variance,
        "sgpa_std_dev": std_dev,
        "assumed_future_sgpa": round(max(0.0, min(10.0, assumed_future_sgpa)), 2),
        "target_scenarios": [item.to_dict() for item in scenarios],
        "graduation_trajectory": [step.to_dict() for step in trajectory],
    }
