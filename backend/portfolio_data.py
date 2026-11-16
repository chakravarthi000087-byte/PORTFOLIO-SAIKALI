"""Portfolio domain dataset for A. Sai Kali Chakravarthi.

Serves as the single source of truth for the Python backend APIs and data
processing pipelines.
"""

from __future__ import annotations

from typing import List

from backend.models import (
    AchievementCard,
    ArchitectureLayer,
    ContactChannel,
    CoreKnowledgeTopic,
    EducationProfile,
    HeroProfile,
    ProjectShowcase,
    QuickStat,
    SemesterMetric,
    SkillItem,
)

OWNER_EMAIL = "chakravarthi000087@gmail.com"
OWNER_PHONE = "+91 8143211120"
OWNER_PHONE_RAW = "8143211120"
GITHUB_URL = "https://github.com/chakravarthi000087-byte"
LINKEDIN_URL = "https://www.linkedin.com/in/anupati-sai-kali-chakravarthi-097178449"
TRIP_GUIDE_URL = "https://jainsmartnavigation.ai.studio"


def get_hero_profile() -> HeroProfile:
    """Return the hero identity and quick-stats configuration."""
    return HeroProfile(
        brand_initials="SC",
        brand_name="Sai Chakravarthi",
        full_name="A. Sai Kali Chakravarthi",
        initials_fallback="AS",
        status_badge="B.Tech CSE (2nd Year, Sem 3) • Jain University",
        summary=(
            "Second-year Computer Science and Engineering student at Jain University, Bengaluru. "
            "Interested in software development and web development, with foundational skills in "
            "Python, Java, SQL, and web technologies—eager to build practical skills through hands-on projects."
        ),
        roles=[
            "B.Tech CSE Student @ Jain University",
            "Aspiring Software Developer",
            "Web Development Enthusiast",
            "Celestia Hackathon Finalist",
        ],
        location="Hyderabad, Telangana",
        university_short="Bengaluru (Jain University)",
        hackathon_badge="Celestia Hackathon Finalist",
        batch_period="B.Tech CSE • 2025–2029",
        github_url=GITHUB_URL,
        linkedin_url=LINKEDIN_URL,
        float_chip_title="8.65 / 8.20 SGPA",
        float_chip_subtitle="Sem 1 & Sem 2",
        quick_stats=[
            QuickStat(value="8.65", label="Semester 1 SGPA", numeric_value=8.65, unit="SGPA"),
            QuickStat(value="8.20", label="Semester 2 SGPA", numeric_value=8.20, unit="SGPA"),
            QuickStat(value="Finalist", label="Celestia Hackathon"),
            QuickStat(value="3 Langs", label="English • Telugu • Hindi", numeric_value=3.0, unit="languages"),
        ],
    )


def get_education_profile() -> EducationProfile:
    """Return structured academic progression and semester metrics."""
    return EducationProfile(
        institution="Jain University, Bengaluru",
        location="Bengaluru, Karnataka",
        degree="B.Tech in Computer Science and Engineering",
        period="2025 – 2029 (Expected)",
        current_year_label="Currently in 2nd Year, 3rd Semester",
        focus="Focus: Software & Web Development",
        current_semester=3,
        total_semesters=8,
        semesters=[
            SemesterMetric(
                semester=1,
                label="Semester 1",
                status="Completed",
                sgpa=8.65,
                progress_percent=86.5,
                credits=20,
            ),
            SemesterMetric(
                semester=2,
                label="Semester 2",
                status="Completed",
                sgpa=8.20,
                progress_percent=82.0,
                credits=22,
            ),
            SemesterMetric(
                semester=3,
                label="Semester 3",
                status="In Progress",
                sgpa=None,
                progress_percent=45.0,
                credits=22,
            ),
        ],
    )


def get_skills_catalog() -> List[SkillItem]:
    """Return the categorized technical skills catalog."""
    return [
        SkillItem(
            id="python",
            name="Python",
            category="languages",
            category_label="Programming Language",
            level="Beginner",
            proficiency=45,
            keywords=["backend", "data processing", "scripting", "oop"],
        ),
        SkillItem(
            id="java",
            name="Java",
            category="languages",
            category_label="Programming Language",
            level="Beginner",
            proficiency=45,
            keywords=["oop", "classes", "algorithms"],
        ),
        SkillItem(
            id="sql",
            name="SQL",
            category="languages",
            category_label="Database Querying",
            level="Beginner",
            proficiency=45,
            keywords=["postgresql", "queries", "relational", "joins"],
        ),
        SkillItem(
            id="html",
            name="HTML",
            category="web",
            category_label="Web Technologies",
            level="Beginner",
            proficiency=50,
            keywords=["semantic markup", "accessibility", "dom"],
        ),
        SkillItem(
            id="css",
            name="CSS",
            category="web",
            category_label="Web Technologies",
            level="Beginner",
            proficiency=48,
            keywords=["flexbox", "grid", "responsive", "theming"],
        ),
        SkillItem(
            id="vscode",
            name="VS Code",
            category="tools",
            category_label="Development Tool",
            level="Intermediate",
            proficiency=76,
            keywords=["ide", "debugging", "extensions"],
        ),
        SkillItem(
            id="git",
            name="Git / GitHub",
            category="tools",
            category_label="Version Control",
            level="Intermediate",
            proficiency=74,
            keywords=["commits", "branching", "repositories"],
        ),
        SkillItem(
            id="colab",
            name="Google Colab",
            category="tools",
            category_label="Cloud Notebook Environment",
            level="Intermediate",
            proficiency=72,
            keywords=["python", "notebooks", "experiments"],
        ),
    ]


def get_core_knowledge_topics() -> List[CoreKnowledgeTopic]:
    """Return foundational computer science topics for interactive inspection."""
    return [
        CoreKnowledgeTopic(
            id="oop",
            title="Object-Oriented Programming (OOP)",
            short_label="Object-Oriented Programming (OOP)",
            description=(
                "Designing modular, reusable code using classes, encapsulation, inheritance, "
                "and polymorphism—applied with Java and Python."
            ),
            applied_in=["Python Backend Models", "Java Coursework", "Modular API Design"],
        ),
        CoreKnowledgeTopic(
            id="dsa",
            title="Data Structures",
            short_label="Data Structures",
            description=(
                "Understanding arrays, linked lists, stacks, queues, trees, and algorithmic "
                "efficiency to solve programming challenges cleanly."
            ),
            applied_in=["Search & Sorting Pipelines", "Graph Routing Concepts", "Hackathon Problems"],
        ),
        CoreKnowledgeTopic(
            id="os",
            title="Operating Systems",
            short_label="Operating Systems",
            description=(
                "Core concepts of processes, threads, scheduling, memory management, and file "
                "systems that power backend and application software."
            ),
            applied_in=["HTTP Server Concurrency", "Subprocess Management", "File I/O"],
        ),
        CoreKnowledgeTopic(
            id="stats",
            title="Statistics",
            short_label="Statistics",
            description=(
                "Analyzing distributions, variance, and data patterns—helpful for reasoning "
                "about metrics, budgets, and computational models."
            ),
            applied_in=["SGPA Trend Analytics", "Skill Distribution Metrics", "Budget Modeling"],
        ),
        CoreKnowledgeTopic(
            id="prob",
            title="Probability",
            short_label="Probability",
            description=(
                "Foundational mathematical reasoning for uncertainty, event modeling, and "
                "analytical problem solving in computer science."
            ),
            applied_in=["Risk Estimation", "Weather Forecast Context", "Algorithmic Analysis"],
        ),
    ]


def get_featured_project() -> ProjectShowcase:
    """Return the Trip Guide project specification and architecture layers."""
    return ProjectShowcase(
        id="trip-guide",
        title="Trip Guide – Travel Planning Platform",
        stage_label="Stage: Architecture & Foundation",
        description=(
            "Designed a travel-planning platform to help users organize trips, create structured itineraries, "
            "and manage travel budgets and expenses. Planned with a modern full-stack architecture combining "
            "Next.js, FastAPI, and PostgreSQL alongside map and weather integrations."
        ),
        tech_tags=[
            "Next.js (Planned)",
            "FastAPI (Planned)",
            "PostgreSQL (Planned)",
            "Map Integration",
            "Weather API",
        ],
        live_url=TRIP_GUIDE_URL,
        github_url=GITHUB_URL,
        layers=[
            ArchitectureLayer(
                id="overview",
                tab_label="Overview",
                title="Core Platform Capabilities",
                summary=(
                    "End-to-end trip organization tailored for travelers managing schedules "
                    "and costs in one place."
                ),
                highlights=[
                    "Trip organization & day-by-day itinerary builder",
                    "Travel budget planning and expense tracking",
                    "Unified architecture foundation ready for iterative buildout",
                ],
                technologies=["Next.js", "FastAPI", "PostgreSQL"],
            ),
            ArchitectureLayer(
                id="frontend",
                tab_label="Frontend",
                title="Next.js Frontend Layer (Planned)",
                summary=(
                    "Responsive client experience for itinerary creation, budget dashboards, "
                    "and interactive views."
                ),
                highlights=[
                    "Clean route-based navigation for trips and expenses",
                    "Interactive itinerary cards and expense summaries",
                    "Responsive layout for desktop & mobile travelers",
                ],
                technologies=["Next.js", "React", "TypeScript"],
            ),
            ArchitectureLayer(
                id="backend",
                tab_label="Backend",
                title="FastAPI Backend Layer (Planned)",
                summary=(
                    "Lightweight, structured Python API service handling core business logic "
                    "and validation."
                ),
                highlights=[
                    "REST endpoints for trips, itinerary items, and budgets",
                    "Schema validation and modular service structure",
                    "Proxy integration for external weather & map services",
                ],
                technologies=["Python", "FastAPI", "Pydantic"],
            ),
            ArchitectureLayer(
                id="data",
                tab_label="Database & APIs",
                title="PostgreSQL + Map & Weather Integrations",
                summary=(
                    "Relational data persistence paired with location and live forecast context."
                ),
                highlights=[
                    "PostgreSQL relational schema for users, trips, and expenses",
                    "Map integration for destination & route visualization",
                    "Weather integration for smarter itinerary planning",
                ],
                technologies=["PostgreSQL", "Maps API", "Weather API"],
            ),
        ],
    )


def get_achievement_cards() -> List[AchievementCard]:
    """Return the achievements, interests, and languages cards."""
    return [
        AchievementCard(
            id="celestia",
            icon="🏆",
            title="Celestia Hackathon",
            description=(
                "Participated in the Celestia Hackathon, advanced to the final round, "
                "and earned a participation certificate—strengthening rapid problem-solving "
                "and teamwork under deadlines."
            ),
            chips=["Final Round", "Certificate Earned"],
            highlight_first_chip=True,
        ),
        AchievementCard(
            id="interests",
            icon="🎯",
            title="Areas of Interest & Soft Skills",
            description=(
                "Focused on turning foundational computer science concepts into clean, "
                "user-friendly software."
            ),
            chips=[
                "Software Development",
                "Web Development",
                "Communication",
                "Adaptability",
                "Time Management",
            ],
        ),
        AchievementCard(
            id="languages",
            icon="🌐",
            title="Languages Spoken",
            description=(
                "Comfortable collaborating in multilingual academic and team environments."
            ),
            chips=["English", "Telugu", "Hindi"],
        ),
    ]


def get_contact_channels() -> List[ContactChannel]:
    """Return direct contact channels for copying or opening links."""
    return [
        ContactChannel(
            id="email",
            label="Email",
            display_value=OWNER_EMAIL,
            action_type="copy",
            action_value=OWNER_EMAIL,
        ),
        ContactChannel(
            id="phone",
            label="Phone",
            display_value=OWNER_PHONE,
            action_type="copy",
            action_value=OWNER_PHONE_RAW,
        ),
        ContactChannel(
            id="linkedin",
            label="LinkedIn",
            display_value="anupati-sai-kali-chakravarthi-097178449",
            action_type="link",
            action_value=LINKEDIN_URL,
        ),
        ContactChannel(
            id="github",
            label="GitHub",
            display_value="github.com/chakravarthi000087-byte",
            action_type="link",
            action_value=GITHUB_URL,
        ),
    ]
