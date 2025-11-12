from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    SentenceBuilderLevel,
    SentenceBuilderSentence,
    SentenceBuilderGameSession,
    UserSentenceProgress
)
import random
import uuid


class Command(BaseCommand):
    help = "Seed the database with Sentence Builder Levels, Sentences, and Demo User Progress"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding Sentence Builder (Enhanced Models)..."))

        # ==========================
        # 1️⃣ Create Level Configurations
        # ==========================
        level_data = [
            # Easy
            {"level_number": 1, "difficulty": "easy", "sentences_required": 3, "time_limit": 180, "points_per_sentence": 10, "unlock_score": 0},
            {"level_number": 2, "difficulty": "easy", "sentences_required": 4, "time_limit": 180, "points_per_sentence": 12, "unlock_score": 30},
            {"level_number": 3, "difficulty": "easy", "sentences_required": 5, "time_limit": 150, "points_per_sentence": 15, "unlock_score": 60},

            # Medium
            {"level_number": 4, "difficulty": "medium", "sentences_required": 4, "time_limit": 150, "points_per_sentence": 20, "unlock_score": 100},
            {"level_number": 5, "difficulty": "medium", "sentences_required": 5, "time_limit": 140, "points_per_sentence": 25, "unlock_score": 150},
            {"level_number": 6, "difficulty": "medium", "sentences_required": 6, "time_limit": 130, "points_per_sentence": 30, "unlock_score": 200},

            # Hard
            {"level_number": 7, "difficulty": "hard", "sentences_required": 5, "time_limit": 120, "points_per_sentence": 35, "unlock_score": 300},
            {"level_number": 8, "difficulty": "hard", "sentences_required": 6, "time_limit": 110, "points_per_sentence": 40, "unlock_score": 400},
            {"level_number": 9, "difficulty": "hard", "sentences_required": 7, "time_limit": 100, "points_per_sentence": 45, "unlock_score": 500},

            # Expert
            {"level_number": 10, "difficulty": "expert", "sentences_required": 8, "time_limit": 90, "points_per_sentence": 50, "unlock_score": 650},
        ]

        levels = {}
        for data in level_data:
            level, _ = SentenceBuilderLevel.objects.get_or_create(
                level_number=data["level_number"], defaults=data
            )
            levels[data["level_number"]] = level
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(levels)} levels."))

        # ==========================
        # 2️⃣ Create Sentences per Level
        # ==========================

        easy_sentences = [
            "The cat is sleeping on the mat.",
            "A dog barks loudly at night.",
            "The bird is flying in the sky.",
            "The cow eats green grass.",
            "The horse runs fast in the field.",
            "The duck swims in the water.",
            "The frog jumps into the pond.",
            "The sheep has soft wool.",
            "The rabbit eats a carrot.",
            "The pig is rolling in the mud.",
            "The hen lays eggs every morning.",
            "The goat climbs the hill.",
            "The bee makes sweet honey.",
            "The monkey climbs the tree.",
            "The puppy plays with a ball.",
            "The kitten drinks milk.",
            "The lion roars in the jungle.",
            "The elephant has a long trunk.",
            "The parrot can talk and sing.",
            "The turtle moves very slowly.",
        ]

        medium_sentences = [
            "I brush my teeth every morning before school.",
            "She eats breakfast with her family.",
            "He rides his bicycle to the park.",
            "We play football in the afternoon.",
            "They read books before going to bed.",
            "Mom cooks dinner for everyone.",
            "Dad waters the plants in the garden.",
            "I take a shower after playing outside.",
            "We clean our room every weekend.",
            "She listens to music while studying.",
            "I help my mom set the table for dinner.",
            "We go shopping at the supermarket on Sundays.",
            "He feeds the dog every morning.",
            "I pack my school bag every night.",
            "We go swimming when it is sunny.",
            "She writes in her diary every day.",
            "They do their homework after lunch.",
            "I drink milk before going to bed.",
            "He plays games with his friends.",
            "We visit our grandparents every holiday.",
        ]

        hard_sentences = [
            "The astronaut floated gracefully inside the space station.",
            "Scientists discovered a new planet beyond our solar system.",
            "The volcano erupted with a loud roar, spewing lava into the sky.",
            "The telescope allows us to see distant stars and galaxies.",
            "Gravity keeps everything anchored to the Earth’s surface.",
            "The experiment proved that plants need sunlight to grow.",
            "Satellites orbit the Earth to help with communication and weather reports.",
            "The engineer designed a rocket that could travel to Mars.",
            "Electricity flows through the wires to power the lights.",
            "The invention of the telephone changed the way people communicate.",
            "Astronomers study the movement of stars and planets.",
            "The scientist mixed chemicals carefully in the laboratory.",
            "The microscope reveals tiny organisms invisible to the naked eye.",
            "The robot performed complex tasks faster than a human.",
            "The researcher collected data from various experiments.",
            "Energy can neither be created nor destroyed, only transformed.",
            "The satellite transmitted images of the Earth from space.",
            "The spacecraft landed safely on the moon’s surface.",
            "Technology continues to evolve at an incredible speed.",
            "Artificial intelligence helps machines learn from experience.",
        ]

        expert_sentences = [
            "The quantum computer processed data faster than any classical machine.",
            "Evolutionary biology explores how species adapt over time.",
            "The physicist formulated a groundbreaking theory of particle behavior.",
            "Dark matter remains one of the universe’s greatest mysteries.",
            "Neuroscientists study how electrical impulses create thoughts.",
            "The mathematician solved an equation unsolved for decades.",
            "The AI system learned to compose symphonies autonomously.",
            "Black holes distort time and space in fascinating ways.",
            "The surgeon performed a successful robotic heart transplant.",
            "Renewable energy sources are crucial for a sustainable future.",
            "Machine learning algorithms improve with every iteration.",
            "Space telescopes provide valuable data about distant galaxies.",
            "Genetic engineering opens new doors in medicine and agriculture.",
            "The Mars rover discovered traces of ancient water.",
            "Astrophysicists simulate the birth of stars in virtual labs.",
            "The chemist synthesized a new compound for clean energy.",
            "Cybersecurity protects sensitive data from digital threats.",
            "Cognitive science bridges psychology and artificial intelligence.",
            "The fusion reactor produced energy more efficiently than expected.",
            "Interstellar travel remains a dream of human exploration.",
        ]

        # Map sentences to levels
        level_sentence_map = {
            (1, 2, 3): easy_sentences,
            (4, 5, 6): medium_sentences,
            (7, 8, 9): hard_sentences,
            (10,): expert_sentences,
        }

        total_sentences = 0
        for level_range, sentence_list in level_sentence_map.items():
            for level_num in level_range:
                level = levels[level_num]
                for text in random.sample(sentence_list, min(20, len(sentence_list))):
                    SentenceBuilderSentence.objects.get_or_create(
                        sentence=text,
                        level=level,
                        defaults={"hint": f"A {level.difficulty} level sentence."},
                    )
                    total_sentences += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Added {total_sentences} sentences across all levels."))

        # ==========================
        # 3️⃣ Create Demo User and Game Session
        # ==========================
        user, _ = User.objects.get_or_create(username="demo_user", defaults={"password": "demo1234"})

        SentenceBuilderGameSession.objects.get_or_create(
            session_id=str(uuid.uuid4()),
            user=user,
            defaults={
                "player_name": "Demo User",
                "current_level": random.randint(1, 5),
                "total_score": random.randint(100, 500),
                "sentences_completed": random.randint(10, 40),
                "perfect_sentences": random.randint(2, 10),
                "total_attempts": random.randint(15, 50),
                "correct_attempts": random.randint(10, 45),
                "time_spent": random.randint(200, 900),
                "is_active": True,
            },
        )

        UserSentenceProgress.objects.get_or_create(
            user=user,
            defaults={
                "highest_level": 4,
                "total_score": 320,
                "total_sentences": 35,
                "perfect_sentences": 8,
                "games_played": 5,
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ Demo user and progress created successfully."))
        self.stdout.write(self.style.SUCCESS("🎯 Sentence Builder enhanced data seeded successfully!"))
