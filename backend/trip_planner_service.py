"""Backend data-processing service for the featured Trip Guide project.

Implements structured itinerary scheduling, travel budget normalization,
expense category aggregation, and readiness scoring in pure Python, mirroring
the planned FastAPI backend architecture showcased in the portfolio.
"""

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


SUPPORTED_EXPENSE_CATEGORIES = (
    "transport",
    "accommodation",
    "food",
    "activities",
    "miscellaneous",
)


@dataclass(frozen=True)
class ItineraryStop:
    """Represents a scheduled activity stop on a specific trip day."""

    day: int
    title: str
    location: str
    start_hour: int
    duration_hours: float
    estimated_cost: float
    category: str = "activities"

    @property
    def end_hour(self) -> float:
        return round(self.start_hour + self.duration_hours, 2)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["end_hour"] = self.end_hour
        return payload


@dataclass(frozen=True)
class ExpenseEntry:
    """Represents a budgeted or incurred travel expense item."""

    title: str
    category: str
    amount: float
    currency: str = "INR"
    day: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TripPlanRequest:
    """Normalized trip planning request consumed by the Trip Guide processor."""

    destination: str
    duration_days: int
    travelers: int
    total_budget: float
    currency: str = "INR"
    stops: List[ItineraryStop] = field(default_factory=list)
    expenses: List[ExpenseEntry] = field(default_factory=list)


def get_sample_trip_plan() -> TripPlanRequest:
    """Return a realistic sample trip plan for Bengaluru -> Coorg itinerary demos."""
    return TripPlanRequest(
        destination="Coorg & Chikmagalur, Karnataka",
        duration_days=3,
        travelers=4,
        total_budget=24000.0,
        currency="INR",
        stops=[
            ItineraryStop(
                day=1,
                title="Morning Departure & Highway Breakfast",
                location="Bengaluru -> Kunigal",
                start_hour=6,
                duration_hours=4.5,
                estimated_cost=3200.0,
                category="transport",
            ),
            ItineraryStop(
                day=1,
                title="Abbey Falls & Coffee Estate Walk",
                location="Madikeri",
                start_hour=14,
                duration_hours=3.0,
                estimated_cost=1400.0,
                category="activities",
            ),
            ItineraryStop(
                day=2,
                title="Raja's Seat Sunrise & Dubare Elephant Camp",
                location="Kushalnagar",
                start_hour=7,
                duration_hours=5.0,
                estimated_cost=2800.0,
                category="activities",
            ),
            ItineraryStop(
                day=2,
                title="Local Kodava Cuisine Dinner",
                location="Madikeri Town",
                start_hour=19,
                duration_hours=2.0,
                estimated_cost=2400.0,
                category="food",
            ),
            ItineraryStop(
                day=3,
                title="Mandalpatti Jeep Trail & Return Drive",
                location="Madikeri -> Bengaluru",
                start_hour=8,
                duration_hours=6.0,
                estimated_cost=4600.0,
                category="transport",
            ),
        ],
        expenses=[
            ExpenseEntry(title="Homestay (2 Nights)", category="accommodation", amount=6800.0, day=1),
            ExpenseEntry(title="Fuel & Toll", category="transport", amount=4200.0, day=1),
            ExpenseEntry(title="Meals & Cafes", category="food", amount=3900.0, day=2),
            ExpenseEntry(title="Entry Passes & Jeep Safari", category="activities", amount=3400.0, day=3),
        ],
    )


def detect_schedule_conflicts(stops: List[ItineraryStop]) -> List[Dict[str, Any]]:
    """Identify overlapping stops on the same itinerary day."""
    by_day: Dict[int, List[ItineraryStop]] = {}
    for stop in stops:
        by_day.setdefault(stop.day, []).append(stop)

    conflicts: List[Dict[str, Any]] = []
    for day, day_stops in sorted(by_day.items()):
        ordered = sorted(day_stops, key=lambda s: (s.start_hour, s.end_hour))
        for idx in range(len(ordered) - 1):
            current = ordered[idx]
            nxt = ordered[idx + 1]
            if current.end_hour > nxt.start_hour:
                overlap_hours = round(current.end_hour - nxt.start_hour, 2)
                conflicts.append({
                    "day": day,
                    "first_stop": current.title,
                    "second_stop": nxt.title,
                    "overlap_hours": overlap_hours,
                })
    return conflicts


def summarize_trip_budget(plan: TripPlanRequest) -> Dict[str, Any]:
    """Aggregate itinerary and explicit expense totals with per-traveler splits."""
    category_totals: Dict[str, float] = {cat: 0.0 for cat in SUPPORTED_EXPENSE_CATEGORIES}
    daily_totals: Dict[int, float] = {day: 0.0 for day in range(1, max(1, plan.duration_days) + 1)}

    for stop in plan.stops:
        cat = stop.category if stop.category in category_totals else "miscellaneous"
        category_totals[cat] = round(category_totals[cat] + max(0.0, stop.estimated_cost), 2)
        if stop.day in daily_totals:
            daily_totals[stop.day] = round(daily_totals[stop.day] + max(0.0, stop.estimated_cost), 2)

    for exp in plan.expenses:
        cat = exp.category if exp.category in category_totals else "miscellaneous"
        category_totals[cat] = round(category_totals[cat] + max(0.0, exp.amount), 2)
        if exp.day in daily_totals:
            daily_totals[exp.day] = round(daily_totals[exp.day] + max(0.0, exp.amount), 2)

    total_estimated = round(sum(category_totals.values()), 2)
    budget = max(0.0, float(plan.total_budget))
    remaining = round(budget - total_estimated, 2)
    utilization = round((total_estimated / budget) * 100.0, 1) if budget > 0 else 0.0
    travelers = max(1, int(plan.travelers))
    per_traveler = round(total_estimated / travelers, 2)
    daily_values = list(daily_totals.values())
    avg_daily_spend = round(statistics.mean(daily_values), 2) if daily_values else 0.0

    if budget <= 0:
        budget_status = "unbudgeted"
    elif remaining < 0:
        budget_status = "over_budget"
    elif utilization >= 85.0:
        budget_status = "tight"
    else:
        budget_status = "healthy"

    return {
        "currency": plan.currency,
        "total_budget": budget,
        "total_estimated_spend": total_estimated,
        "remaining_budget": remaining,
        "budget_utilization_percent": utilization,
        "budget_status": budget_status,
        "per_traveler_cost": per_traveler,
        "average_daily_spend": avg_daily_spend,
        "category_breakdown": category_totals,
        "daily_spend": [
            {"day": day, "amount": amount}
            for day, amount in sorted(daily_totals.items())
        ],
    }


def parse_trip_plan_payload(payload: Dict[str, Any]) -> Tuple[Optional[TripPlanRequest], List[str]]:
    """Validate and coerce an incoming JSON trip payload into a TripPlanRequest."""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return None, ["Trip payload must be a JSON object."]

    destination = str(payload.get("destination", "")).strip()
    if len(destination) < 2:
        errors.append("Destination must be at least 2 characters long.")

    try:
        duration_days = int(payload.get("duration_days", 1))
        travelers = int(payload.get("travelers", 1))
        total_budget = float(payload.get("total_budget", 0.0))
    except (TypeError, ValueError):
        errors.append("duration_days, travelers, and total_budget must be numeric.")
        return None, errors

    if duration_days < 1 or duration_days > 60:
        errors.append("duration_days must be between 1 and 60.")
    if travelers < 1 or travelers > 50:
        errors.append("travelers must be between 1 and 50.")
    if total_budget < 0:
        errors.append("total_budget cannot be negative.")

    stops: List[ItineraryStop] = []
    for raw_stop in payload.get("stops", []) or []:
        if not isinstance(raw_stop, dict):
            errors.append("Each itinerary stop must be an object.")
            continue
        try:
            stops.append(
                ItineraryStop(
                    day=max(1, int(raw_stop.get("day", 1))),
                    title=str(raw_stop.get("title", "Stop")).strip()[:120],
                    location=str(raw_stop.get("location", destination)).strip()[:120],
                    start_hour=max(0, min(23, int(raw_stop.get("start_hour", 9)))),
                    duration_hours=max(0.5, float(raw_stop.get("duration_hours", 1.0))),
                    estimated_cost=max(0.0, float(raw_stop.get("estimated_cost", 0.0))),
                    category=str(raw_stop.get("category", "activities")).strip().lower(),
                )
            )
        except (TypeError, ValueError):
            errors.append("Invalid numeric field inside itinerary stops.")

    expenses: List[ExpenseEntry] = []
    for raw_exp in payload.get("expenses", []) or []:
        if not isinstance(raw_exp, dict):
            errors.append("Each expense entry must be an object.")
            continue
        try:
            expenses.append(
                ExpenseEntry(
                    title=str(raw_exp.get("title", "Expense")).strip()[:120],
                    category=str(raw_exp.get("category", "miscellaneous")).strip().lower(),
                    amount=max(0.0, float(raw_exp.get("amount", 0.0))),
                    currency=str(payload.get("currency", "INR")).strip().upper()[:6],
                    day=max(1, int(raw_exp.get("day", 1))),
                )
            )
        except (TypeError, ValueError):
            errors.append("Invalid numeric field inside expenses.")

    if errors:
        return None, errors

    return (
        TripPlanRequest(
            destination=destination[:140],
            duration_days=duration_days,
            travelers=travelers,
            total_budget=total_budget,
            currency=str(payload.get("currency", "INR")).strip().upper()[:6] or "INR",
            stops=stops,
            expenses=expenses,
        ),
        [],
    )


def evaluate_trip_plan(plan: Optional[TripPlanRequest] = None) -> Dict[str, Any]:
    """Run full itinerary validation, conflict detection, and budget analytics."""
    target_plan = plan or get_sample_trip_plan()
    conflicts = detect_schedule_conflicts(target_plan.stops)
    budget_summary = summarize_trip_budget(target_plan)

    scheduled_days = {stop.day for stop in target_plan.stops}
    day_coverage = round(
        (len(scheduled_days) / max(1, target_plan.duration_days)) * 100.0,
        1,
    )

    return {
        "destination": target_plan.destination,
        "duration_days": target_plan.duration_days,
        "travelers": target_plan.travelers,
        "stop_count": len(target_plan.stops),
        "expense_count": len(target_plan.expenses),
        "day_coverage_percent": min(100.0, day_coverage),
        "schedule_conflicts": conflicts,
        "has_conflicts": len(conflicts) > 0,
        "budget_summary": budget_summary,
        "itinerary_stops": [stop.to_dict() for stop in target_plan.stops],
    }
