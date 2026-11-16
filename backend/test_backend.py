"""Unit tests for the portfolio Python backend logic and data processing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from backend.analytics_engine import (
    analyze_project_architecture,
    analyze_repository_languages,
    compute_academic_analytics,
    filter_and_analyze_skills,
    lookup_knowledge_topic,
)
from backend.cgpa_projector import (
    build_graduation_trajectory,
    generate_academic_projection_report,
    solve_target_cgpa_scenarios,
)
from backend.contact_processor import process_contact_submission
from backend.router import dispatch_request
from backend.trip_planner_service import (
    ItineraryStop,
    detect_schedule_conflicts,
    evaluate_trip_plan,
    parse_trip_plan_payload,
)


class PortfolioBackendTests(unittest.TestCase):
    """Verifies academic analytics, projections, Trip Guide processing, and routing."""

    def test_academic_analytics_cgpa(self) -> None:
        stats = compute_academic_analytics()
        self.assertEqual(stats["completed_semesters"], 2)
        self.assertEqual(stats["total_credits_completed"], 42)
        self.assertEqual(stats["degree_progress_percent"], 37.5)
        self.assertAlmostEqual(stats["mean_sgpa"], 8.43, places=2)
        self.assertGreaterEqual(stats["cumulative_cgpa"], 8.0)

    def test_cgpa_projector_scenarios_and_trajectory(self) -> None:
        scenarios = solve_target_cgpa_scenarios(targets=[8.5, 9.0, 10.0])
        self.assertEqual(len(scenarios), 3)
        self.assertTrue(scenarios[0].achievable)
        self.assertFalse(scenarios[2].achievable)

        trajectory = build_graduation_trajectory(assumed_future_sgpa=8.8)
        self.assertEqual(len(trajectory), 8)
        self.assertEqual(trajectory[-1].completion_percent, 100.0)

        report = generate_academic_projection_report(assumed_future_sgpa=8.7)
        self.assertEqual(report["total_semesters"], 8)
        self.assertGreater(report["remaining_credits"], 0)

    def test_skill_filtering_and_sorting(self) -> None:
        langs = filter_and_analyze_skills(category="languages")
        self.assertEqual(langs["matched_count"], 3)
        self.assertTrue(all(item["category"] == "languages" for item in langs["items"]))

        sorted_tools = filter_and_analyze_skills(category="tools", sort_by="proficiency")
        proficiencies = [item["proficiency"] for item in sorted_tools["items"]]
        self.assertEqual(proficiencies, sorted(proficiencies, reverse=True))

    def test_knowledge_lookup_and_project_architecture(self) -> None:
        oop = lookup_knowledge_topic(topic_id="oop")
        self.assertTrue(oop["found"])
        self.assertIn("Object-Oriented", oop["selected"]["title"])

        missing = lookup_knowledge_topic(topic_id="nonexistent")
        self.assertFalse(missing["found"])

        arch = analyze_project_architecture(layer_id="backend")
        self.assertEqual(arch["layer_count"], 4)
        self.assertEqual(arch["selected_layer"]["id"], "backend")

    def test_trip_guide_itinerary_and_budget_engine(self) -> None:
        sample = evaluate_trip_plan()
        self.assertFalse(sample["has_conflicts"])
        self.assertEqual(sample["budget_summary"]["budget_status"], "over_budget")

        overlapping = [
            ItineraryStop(day=1, title="Stop A", location="X", start_hour=9, duration_hours=3.0, estimated_cost=100),
            ItineraryStop(day=1, title="Stop B", location="Y", start_hour=11, duration_hours=2.0, estimated_cost=200),
        ]
        conflicts = detect_schedule_conflicts(overlapping)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["overlap_hours"], 1.0)

        parsed, errors = parse_trip_plan_payload({
            "destination": "Mysuru, Karnataka",
            "duration_days": 2,
            "travelers": 2,
            "total_budget": 10000,
            "stops": [{"day": 1, "title": "Mysuru Palace", "start_hour": 10, "duration_hours": 2, "estimated_cost": 800}],
            "expenses": [{"title": "Hotel", "category": "accommodation", "amount": 3200, "day": 1}],
        })
        self.assertEqual(errors, [])
        self.assertIsNotNone(parsed)
        evaluated = evaluate_trip_plan(parsed)
        self.assertEqual(evaluated["budget_summary"]["budget_status"], "healthy")
        self.assertEqual(evaluated["budget_summary"]["per_traveler_cost"], 2000.0)

    def test_contact_validation_and_sanitization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = Path(tmpdir) / "contacts.jsonl"

            bad_status, bad_body = process_contact_submission(
                {"name": "A", "email": "not-an-email", "message": "hi"},
                store_path=store,
            )
            self.assertEqual(bad_status, 400)
            self.assertFalse(bad_body["ok"])
            self.assertGreaterEqual(len(bad_body["errors"]), 2)

            ok_status, ok_body = process_contact_submission(
                {
                    "name": "<b>Recruiter</b>",
                    "email": "recruiter@example.com",
                    "message": "Interested in discussing an internship opportunity!",
                },
                store_path=store,
            )
            self.assertEqual(ok_status, 201)
            self.assertTrue(ok_body["ok"])
            self.assertTrue(ok_body["persisted_to_disk"])
            self.assertIn("mailto:chakravarthi000087@gmail.com", ok_body["mailto_url"])
            self.assertTrue(store.exists())

    def test_router_endpoints(self) -> None:
        status, _, health = dispatch_request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(health["ok"])

        status, _, portfolio = dispatch_request("GET", "/api/portfolio")
        self.assertEqual(status, 200)
        self.assertEqual(portfolio["hero"]["full_name"], "A. Sai Kali Chakravarthi")

        status, _, proj = dispatch_request("GET", "/api/analytics/projection?assumed_sgpa=8.8")
        self.assertEqual(status, 200)
        self.assertEqual(proj["assumed_future_sgpa"], 8.8)

        status, _, trip = dispatch_request("GET", "/api/trip-guide")
        self.assertEqual(status, 200)
        self.assertIn("budget_summary", trip)

        payload = json.dumps({
            "name": "Sai Test",
            "email": "test@example.com",
            "message": "Testing the Python backend route handler.",
        }).encode("utf-8")
        status, _, contact_resp = dispatch_request("POST", "/api/contact", body_bytes=payload)
        self.assertEqual(status, 201)
        self.assertTrue(contact_resp["ok"])

        status, _, not_found = dispatch_request("GET", "/api/does-not-exist")
        self.assertEqual(status, 404)
        self.assertFalse(not_found["ok"])

    def test_repository_language_scanner(self) -> None:
        report = analyze_repository_languages()
        self.assertGreater(report["total_bytes"], 0)
        self.assertGreaterEqual(report["python_percentage"], 50.0)


if __name__ == "__main__":
    unittest.main()
