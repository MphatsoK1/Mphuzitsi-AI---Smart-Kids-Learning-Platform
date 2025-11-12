from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    MathGameLevel,
    MathGameProblem,
    MathGameSession,
    UserMathProgress,
)
import random
import uuid


class Command(BaseCommand):
    help = "Seed the database with Math Game levels, problems, demo session, and progress."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding Math Game data..."))

        # ============================================================
        # 1️⃣ CREATE LEVELS
        # ============================================================
        levels_data = [
            # Easy (1–10)
            {"level_number": 1, "difficulty": "easy", "operations": ["+"], "number_range_min": 1, "number_range_max": 10, "problems_required": 10, "time_limit": 180, "points_per_problem": 10, "unlock_score": 0},
            {"level_number": 2, "difficulty": "easy", "operations": ["+", "-"], "number_range_min": 1, "number_range_max": 15, "problems_required": 10, "time_limit": 170, "points_per_problem": 12, "unlock_score": 30},

            # Medium (10–50)
            {"level_number": 3, "difficulty": "medium", "operations": ["+", "-", "×"], "number_range_min": 5, "number_range_max": 30, "problems_required": 12, "time_limit": 150, "points_per_problem": 15, "unlock_score": 60},
            {"level_number": 4, "difficulty": "medium", "operations": ["+", "-", "×"], "number_range_min": 10, "number_range_max": 50, "problems_required": 12, "time_limit": 140, "points_per_problem": 20, "unlock_score": 120},

            # Hard (50–100)
            {"level_number": 5, "difficulty": "hard", "operations": ["+", "-", "×", "÷"], "number_range_min": 20, "number_range_max": 100, "problems_required": 15, "time_limit": 130, "points_per_problem": 25, "unlock_score": 200},
            {"level_number": 6, "difficulty": "hard", "operations": ["+", "-", "×", "÷"], "number_range_min": 30, "number_range_max": 120, "problems_required": 15, "time_limit": 120, "points_per_problem": 30, "unlock_score": 300},

            # Expert (100–500)
            {"level_number": 7, "difficulty": "expert", "operations": ["+", "-", "×", "÷"], "number_range_min": 50, "number_range_max": 500, "problems_required": 20, "time_limit": 100, "points_per_problem": 40, "unlock_score": 400},
            {"level_number": 8, "difficulty": "expert", "operations": ["+", "-", "×", "÷"], "number_range_min": 100, "number_range_max": 1000, "problems_required": 20, "time_limit": 90, "points_per_problem": 50, "unlock_score": 600},
        ]

        levels = {}
        for data in levels_data:
            level, _ = MathGameLevel.objects.get_or_create(
                level_number=data["level_number"],
                defaults=data,
            )
            levels[level.level_number] = level

        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(levels)} Math Game levels."))

        # ============================================================
        # 2️⃣ CREATE PROBLEMS FOR EACH LEVEL
        # ============================================================

        def generate_problem(a, b, operation):
            """Generate problem text and correct answer."""
            if operation == "+":
                return f"{a} + {b}", a + b
            elif operation == "-":
                return f"{a} - {b}", a - b
            elif operation in ["×", "*"]:
                return f"{a} × {b}", a * b
            elif operation in ["÷", "/"]:
                # Avoid division by zero and ensure clean division
                if b == 0:
                    b = 1
                answer = a // b
                return f"{a} ÷ {b}", answer
            return f"{a} + {b}", a + b

        total_created = 0

        for level in levels.values():
            problems_to_create = level.problems_required
            existing = MathGameProblem.objects.filter(level=level).count()

            if existing >= problems_to_create:
                self.stdout.write(f"Level {level.level_number} already has problems.")
                continue

            for _ in range(problems_to_create):
                a = random.randint(level.number_range_min, level.number_range_max)
                b = random.randint(level.number_range_min, level.number_range_max)
                operation = random.choice(level.operations)

                text, answer = generate_problem(a, b, operation)
                MathGameProblem.objects.get_or_create(
                    problem_text=text,
                    correct_answer=answer,
                    operation=operation,
                    level=level,
                    defaults={"hint": f"Solve the {operation} operation."},
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {total_created} math problems."))

        # ============================================================
        # 3️⃣ CREATE DEMO USER + GAME SESSION + PROGRESS
        # ============================================================

        user, _ = User.objects.get_or_create(username="math_demo_user", defaults={"password": "math1234"})

        MathGameSession.objects.get_or_create(
            session_id=str(uuid.uuid4()),
            user=user,
            defaults={
                "player_name": "Math Demo User",
                "current_level": random.randint(1, 4),
                "total_score": random.randint(100, 500),
                "problems_completed": random.randint(10, 50),
                "perfect_streak": random.randint(1, 5),
                "total_attempts": random.randint(15, 60),
                "correct_attempts": random.randint(10, 55),
                "time_spent": random.randint(100, 800),
                "is_active": True,
            },
        )

        UserMathProgress.objects.get_or_create(
            user=user,
            defaults={
                "highest_level": 4,
                "total_score": 350,
                "total_problems": 60,
                "perfect_streaks": 8,
                "games_played": 5,
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ Demo Math Game user and progress created successfully."))
        self.stdout.write(self.style.SUCCESS("🎯 Math Game data seeded successfully!"))
