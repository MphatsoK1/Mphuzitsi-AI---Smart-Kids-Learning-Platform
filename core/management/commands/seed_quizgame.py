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

        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} quiz categories."))

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
                {
                    "question": "What do we use to write on paper?",
                    "options": ["Spoon", "Pen", "Fork", "Plate"],
                    "answer": "B",
                    "explanation": "A pen is used to write on paper."
                },
                {
                    "question": "Which fruit is red and round?",
                    "options": ["Banana", "Apple", "Orange", "Grape"],
                    "answer": "B",
                    "explanation": "An apple is red and round."
                },
                {
                    "question": "How many legs does a cat have?",
                    "options": ["2", "3", "4", "5"],
                    "answer": "C",
                    "explanation": "A cat has 4 legs."
                },
                {
                    "question": "What do we use to see?",
                    "options": ["Ears", "Eyes", "Nose", "Mouth"],
                    "answer": "B",
                    "explanation": "We use our eyes to see."
                },
                {
                    "question": "Which animal says 'Moo'?",
                    "options": ["Dog", "Cat", "Cow", "Duck"],
                    "answer": "C",
                    "explanation": "A cow says 'Moo'."
                },
                {
                    "question": "What comes after Monday?",
                    "options": ["Sunday", "Tuesday", "Wednesday", "Friday"],
                    "answer": "B",
                    "explanation": "Tuesday comes after Monday."
                },
                {
                    "question": "How many fingers do we have on one hand?",
                    "options": ["3", "4", "5", "6"],
                    "answer": "C",
                    "explanation": "We have 5 fingers on one hand."
                },
                {
                    "question": "What do we drink when we are thirsty?",
                    "options": ["Food", "Water", "Clothes", "Toys"],
                    "answer": "B",
                    "explanation": "We drink water when we are thirsty."
                },
                {
                    "question": "Which season is the coldest?",
                    "options": ["Summer", "Spring", "Winter", "Fall"],
                    "answer": "C",
                    "explanation": "Winter is the coldest season."
                },
                {
                    "question": "What do we use to brush our teeth?",
                    "options": ["Spoon", "Toothbrush", "Fork", "Plate"],
                    "answer": "B",
                    "explanation": "We use a toothbrush to brush our teeth."
                },
                {
                    "question": "How many months are in a year?",
                    "options": ["10", "11", "12", "13"],
                    "answer": "C",
                    "explanation": "There are 12 months in a year."
                },
                {
                    "question": "Which animal lives in water?",
                    "options": ["Dog", "Cat", "Fish", "Bird"],
                    "answer": "C",
                    "explanation": "Fish live in water."
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
                {
                    "question": "What is the largest ocean on Earth?",
                    "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
                    "answer": "D",
                    "explanation": "The Pacific Ocean is the largest ocean on Earth."
                },
                {
                    "question": "Which planet is closest to the Sun?",
                    "options": ["Venus", "Mercury", "Earth", "Mars"],
                    "answer": "B",
                    "explanation": "Mercury is the closest planet to the Sun."
                },
                {
                    "question": "What do bees make?",
                    "options": ["Milk", "Honey", "Butter", "Cheese"],
                    "answer": "B",
                    "explanation": "Bees make honey."
                },
                {
                    "question": "How many continents are there?",
                    "options": ["5", "6", "7", "8"],
                    "answer": "C",
                    "explanation": "There are 7 continents on Earth."
                },
                {
                    "question": "What is the hardest natural substance?",
                    "options": ["Gold", "Diamond", "Silver", "Iron"],
                    "answer": "B",
                    "explanation": "Diamond is the hardest natural substance."
                },
                {
                    "question": "Which animal is the largest mammal?",
                    "options": ["Elephant", "Blue Whale", "Giraffe", "Hippo"],
                    "answer": "B",
                    "explanation": "The blue whale is the largest mammal."
                },
                {
                    "question": "What is the main gas in Earth's atmosphere?",
                    "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
                    "answer": "B",
                    "explanation": "Nitrogen makes up about 78% of Earth's atmosphere."
                },
                {
                    "question": "How many sides does a triangle have?",
                    "options": ["2", "3", "4", "5"],
                    "answer": "B",
                    "explanation": "A triangle has 3 sides."
                },
                {
                    "question": "What do we call a baby cat?",
                    "options": ["Puppy", "Kitten", "Cub", "Chick"],
                    "answer": "B",
                    "explanation": "A baby cat is called a kitten."
                },
                {
                    "question": "Which season comes after winter?",
                    "options": ["Summer", "Spring", "Fall", "Autumn"],
                    "answer": "B",
                    "explanation": "Spring comes after winter."
                },
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "answer": "C",
                    "explanation": "Paris is the capital of France."
                },
                {
                    "question": "How many minutes are in an hour?",
                    "options": ["30", "45", "60", "90"],
                    "answer": "C",
                    "explanation": "There are 60 minutes in an hour."
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
                {
                    "question": "What is the smallest prime number?",
                    "options": ["0", "1", "2", "3"],
                    "answer": "C",
                    "explanation": "2 is the smallest prime number."
                },
                {
                    "question": "Which mountain is the tallest in the world?",
                    "options": ["K2", "Mount Everest", "Kilimanjaro", "Mount Fuji"],
                    "answer": "B",
                    "explanation": "Mount Everest is the tallest mountain in the world."
                },
                {
                    "question": "What is the chemical formula for water?",
                    "options": ["H2O", "CO2", "O2", "NaCl"],
                    "answer": "A",
                    "explanation": "The chemical formula for water is H2O."
                },
                {
                    "question": "Which country is known as the Land of the Rising Sun?",
                    "options": ["China", "Japan", "Korea", "Thailand"],
                    "answer": "B",
                    "explanation": "Japan is known as the Land of the Rising Sun."
                },
                {
                    "question": "What is the speed of light in vacuum?",
                    "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "600,000 km/s"],
                    "answer": "A",
                    "explanation": "The speed of light in vacuum is approximately 300,000 km/s."
                },
                {
                    "question": "Which planet has the most moons?",
                    "options": ["Jupiter", "Saturn", "Uranus", "Neptune"],
                    "answer": "B",
                    "explanation": "Saturn has the most moons in our solar system."
                },
                {
                    "question": "What is the largest desert in the world?",
                    "options": ["Gobi", "Sahara", "Antarctic", "Arabian"],
                    "answer": "C",
                    "explanation": "The Antarctic Desert is the largest desert in the world."
                },
                {
                    "question": "Which war was fought between 1861 and 1865?",
                    "options": ["World War I", "World War II", "American Civil War", "Revolutionary War"],
                    "answer": "C",
                    "explanation": "The American Civil War was fought from 1861 to 1865."
                },
                {
                    "question": "What is the capital of Australia?",
                    "options": ["Sydney", "Melbourne", "Canberra", "Perth"],
                    "answer": "C",
                    "explanation": "Canberra is the capital of Australia."
                },
                {
                    "question": "Which element has the symbol 'Fe'?",
                    "options": ["Iron", "Fluorine", "Fermium", "Francium"],
                    "answer": "A",
                    "explanation": "Fe is the chemical symbol for Iron."
                },
                {
                    "question": "What is the longest river in the world?",
                    "options": ["Amazon", "Nile", "Mississippi", "Yangtze"],
                    "answer": "B",
                    "explanation": "The Nile River is the longest river in the world."
                },
                {
                    "question": "Which scientist discovered gravity?",
                    "options": ["Einstein", "Newton", "Galileo", "Darwin"],
                    "answer": "B",
                    "explanation": "Sir Isaac Newton discovered and described gravity."
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
                {
                    "question": "What is the square root of 144?",
                    "options": ["10", "11", "12", "13"],
                    "answer": "C",
                    "explanation": "The square root of 144 is 12 (12 × 12 = 144)."
                },
                {
                    "question": "Which theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides?",
                    "options": ["Pythagorean", "Euclidean", "Fermat's", "Descartes'"],
                    "answer": "A",
                    "explanation": "The Pythagorean theorem describes the relationship in right triangles."
                },
                {
                    "question": "What is the atomic number of carbon?",
                    "options": ["4", "5", "6", "7"],
                    "answer": "C",
                    "explanation": "Carbon has an atomic number of 6."
                },
                {
                    "question": "Which planet is farthest from the Sun?",
                    "options": ["Uranus", "Neptune", "Pluto", "Saturn"],
                    "answer": "B",
                    "explanation": "Neptune is the farthest planet from the Sun in our solar system."
                },
                {
                    "question": "What is the value of pi (π) to two decimal places?",
                    "options": ["3.12", "3.14", "3.16", "3.18"],
                    "answer": "B",
                    "explanation": "Pi (π) is approximately 3.14."
                },
                {
                    "question": "Which programming language was created by Guido van Rossum?",
                    "options": ["Java", "Python", "C++", "JavaScript"],
                    "answer": "B",
                    "explanation": "Python was created by Guido van Rossum."
                },
                {
                    "question": "What is the largest prime number less than 20?",
                    "options": ["17", "18", "19", "16"],
                    "answer": "C",
                    "explanation": "19 is the largest prime number less than 20."
                },
                {
                    "question": "Which element makes up most of the Sun?",
                    "options": ["Helium", "Hydrogen", "Oxygen", "Carbon"],
                    "answer": "B",
                    "explanation": "Hydrogen makes up about 73% of the Sun's mass."
                },
                {
                    "question": "What is the derivative of x²?",
                    "options": ["x", "2x", "x²", "2x²"],
                    "answer": "B",
                    "explanation": "The derivative of x² is 2x."
                },
                {
                    "question": "Which country has the most time zones?",
                    "options": ["Russia", "United States", "China", "France"],
                    "answer": "A",
                    "explanation": "Russia spans 11 time zones, the most of any country."
                },
                {
                    "question": "What is the smallest unit of matter?",
                    "options": ["Molecule", "Atom", "Electron", "Proton"],
                    "answer": "B",
                    "explanation": "An atom is the smallest unit of matter that retains chemical properties."
                },
                {
                    "question": "Which mathematical constant is approximately 2.718?",
                    "options": ["Pi (π)", "Euler's number (e)", "Golden ratio (φ)", "Square root of 2"],
                    "answer": "B",
                    "explanation": "Euler's number (e) is approximately 2.718."
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

        self.stdout.write(self.style.SUCCESS(f"Created {total_created} quiz questions."))

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

        self.stdout.write(self.style.SUCCESS("Quiz levels created successfully."))

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

        self.stdout.write(self.style.SUCCESS("Demo quiz user and progress created successfully."))
        self.stdout.write(self.style.SUCCESS("Quiz Game data seeded successfully!"))
