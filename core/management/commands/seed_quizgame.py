from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    QuizCategory,
    QuizQuestion,
    QuizLevel,
    QuizGameSession,
    UserQuizProgress
)
import random
import uuid


class Command(BaseCommand):
    help = "Seed the database with Quiz Game categories, questions, levels, and demo data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding Quiz Game data..."))

        # ============================================================
        # 1️⃣ CREATE CATEGORIES
        # ============================================================
        categories_data = [
            {"name": "General Knowledge", "difficulty": "easy", "description": "Basic facts and trivia for beginners.", "color": "#10B981", "icon": "🌍"},
            {"name": "Science & Nature", "difficulty": "medium", "description": "Explore the wonders of science and the natural world.", "color": "#3B82F6", "icon": "🧬"},
            {"name": "History & Geography", "difficulty": "hard", "description": "Challenging questions about world history and geography.", "color": "#F59E0B", "icon": "📜"},
            {"name": "Advanced IQ Challenge", "difficulty": "expert", "description": "Test your intelligence with tricky and logical questions.", "color": "#EF4444", "icon": "🧠"},
        ]

        categories = {}
        for data in categories_data:
            category, _ = QuizCategory.objects.get_or_create(
                name=data["name"],
                defaults=data
            )
            categories[data["difficulty"]] = category

        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(categories)} quiz categories."))

        # ============================================================
        # 2️⃣ CREATE QUESTIONS FOR EACH CATEGORY
        # ============================================================

        sample_questions = {
            "easy": [
                {
                    "question": "What color is the sky on a clear day?",
                    "options": ["Blue", "Green", "Red", "Yellow"],
                    "answer": "A",
                    "explanation": "The sky appears blue due to the scattering of sunlight by the atmosphere."
                },
                {
                    "question": "Which animal is known as the 'King of the Jungle'?",
                    "options": ["Elephant", "Tiger", "Lion", "Giraffe"],
                    "answer": "C",
                    "explanation": "The lion is often called the King of the Jungle."
                },
                {
                    "question": "How many days are there in a week?",
                    "options": ["5", "6", "7", "8"],
                    "answer": "C",
                    "explanation": "There are 7 days in a week."
                },
            ],
            "medium": [
                {
                    "question": "What planet is known as the Red Planet?",
                    "options": ["Earth", "Mars", "Venus", "Jupiter"],
                    "answer": "B",
                    "explanation": "Mars is called the Red Planet due to its reddish appearance."
                },
                {
                    "question": "What gas do plants absorb from the atmosphere?",
                    "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
                    "answer": "B",
                    "explanation": "Plants use carbon dioxide during photosynthesis."
                },
                {
                    "question": "How many bones are in the adult human body?",
                    "options": ["206", "210", "201", "205"],
                    "answer": "A",
                    "explanation": "The adult human skeleton has 206 bones."
                },
            ],
            "hard": [
                {
                    "question": "Who was the first President of the United States?",
                    "options": ["Abraham Lincoln", "George Washington", "Thomas Jefferson", "John Adams"],
                    "answer": "B",
                    "explanation": "George Washington served as the first U.S. President from 1789 to 1797."
                },
                {
                    "question": "In which year did World War II end?",
                    "options": ["1943", "1944", "1945", "1946"],
                    "answer": "C",
                    "explanation": "World War II ended in 1945."
                },
                {
                    "question": "Which river flows through the city of Cairo?",
                    "options": ["Amazon", "Nile", "Danube", "Mississippi"],
                    "answer": "B",
                    "explanation": "The Nile River passes through Cairo, Egypt."
                },
            ],
            "expert": [
                {
                    "question": "What is the chemical symbol for gold?",
                    "options": ["Gd", "Au", "Ag", "Go"],
                    "answer": "B",
                    "explanation": "The chemical symbol for gold is 'Au'."
                },
                {
                    "question": "Which scientist proposed the three laws of motion?",
                    "options": ["Einstein", "Newton", "Galileo", "Kepler"],
                    "answer": "B",
                    "explanation": "Sir Isaac Newton formulated the three laws of motion."
                },
                {
                    "question": "What is the capital city of Iceland?",
                    "options": ["Reykjavík", "Oslo", "Helsinki", "Copenhagen"],
                    "answer": "A",
                    "explanation": "Reykjavík is the capital and largest city of Iceland."
                },
            ],
        }

        total_created = 0
        for difficulty, questions in sample_questions.items():
            category = categories[difficulty]
            for q in questions:
                QuizQuestion.objects.get_or_create(
                    category=category,
                    question_text=q["question"],
                    defaults={
                        "option_a": q["options"][0],
                        "option_b": q["options"][1],
                        "option_c": q["options"][2],
                        "option_d": q["options"][3],
                        "correct_option": q["answer"],
                        "explanation": q["explanation"],
                        "points": random.randint(5, 15),
                    },
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {total_created} quiz questions."))

        # ============================================================
        # 3️⃣ CREATE LEVELS FOR EACH CATEGORY
        # ============================================================
        level_number = 1
        for cat in categories.values():
            QuizLevel.objects.get_or_create(
                level_number=level_number,
                category=cat,
                defaults={
                    "questions_required": 5,
                    "time_limit": 300,
                    "unlock_score": (level_number - 1) * 100,
                },
            )
            level_number += 1

        self.stdout.write(self.style.SUCCESS("✅ Quiz levels created successfully."))

        # ============================================================
        # 4️⃣ DEMO USER, SESSION, AND PROGRESS
        # ============================================================
        user, _ = User.objects.get_or_create(username="quiz_demo_user", defaults={"password": "quiz1234"})

        QuizGameSession.objects.get_or_create(
            session_id=str(uuid.uuid4()),
            user=user,
            defaults={
                "player_name": "Quiz Demo User",
                "current_level": random.randint(1, 4),
                "total_score": random.randint(100, 400),
                "questions_answered": random.randint(5, 20),
                "correct_answers": random.randint(3, 15),
                "perfect_streak": random.randint(0, 5),
                "time_spent": random.randint(100, 600),
                "is_active": True,
            },
        )

        UserQuizProgress.objects.get_or_create(
            user=user,
            defaults={
                "highest_level": 2,
                "total_score": 250,
                "total_questions": 30,
                "correct_answers": 20,
                "perfect_quizzes": 3,
                "games_played": 4,
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ Demo quiz user and progress created successfully."))
        self.stdout.write(self.style.SUCCESS("🎯 Quiz Game data seeded successfully!"))
