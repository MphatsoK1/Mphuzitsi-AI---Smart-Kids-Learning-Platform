from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    WordSearchLevel,
    WordSearchCategory,
    WordSearchPuzzle,
)
import random
import string
import json


class Command(BaseCommand):
    help = "Load kid-friendly Word Search data (easy levels, fun themes, colorful categories)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🎮 Loading Word Search Data for Kids..."))

        # ======================
        # 1️⃣ Create Levels
        # ======================
        levels = [
            {"level_number": 1, "difficulty": "easy", "grid_size": 6, "word_count": 5, "time_limit": 120, "points_per_word": 5},
            {"level_number": 2, "difficulty": "easy", "grid_size": 8, "word_count": 6, "time_limit": 150, "points_per_word": 6},
            {"level_number": 3, "difficulty": "medium", "grid_size": 10, "word_count": 8, "time_limit": 180, "points_per_word": 8},
        ]
        WordSearchLevel.objects.all().delete()
        for lvl in levels:
            WordSearchLevel.objects.create(**lvl)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(levels)} levels"))

        # ======================
        # 2️⃣ Create Categories
        # ======================
        categories = [
            {"name": "Animals", "description": "Find names of cute animals!", "color": "#F87171", "icon": "🐶"},
            {"name": "Fruits", "description": "Juicy and sweet fruit words!", "color": "#34D399", "icon": "🍎"},
            {"name": "Colors", "description": "Find all the colorful words!", "color": "#60A5FA", "icon": "🎨"},
            {"name": "Toys", "description": "Playtime fun with toy names!", "color": "#FBBF24", "icon": "🧸"},
        ]
        WordSearchCategory.objects.all().delete()
        category_objs = [WordSearchCategory.objects.create(**c) for c in categories]
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(category_objs)} categories"))

        # ======================
        # 3️⃣ Create Puzzles
        # ======================
        puzzles_data = {
            "Animals": [["cat", "dog", "cow", "bee", "ant"], ["lion", "bear", "frog", "owl", "bat"]],
            "Fruits": [["apple", "pear", "mango", "kiwi", "lime"], ["grape", "melon", "plum", "fig", "date"]],
            "Colors": [["red", "blue", "green", "pink", "gold"], ["black", "white", "gray", "cyan", "teal"]],
            "Toys": [["ball", "car", "doll", "kite", "lego"], ["train", "drum", "puzzle", "block", "bear"]],
        }

        WordSearchPuzzle.objects.all().delete()
        for category in category_objs:
            for i, word_list in enumerate(puzzles_data[category.name]):
                # Simple fake grid generator (for demo purposes)
                grid_size = 6
                grid_data = [[random.choice(string.ascii_uppercase) for _ in range(grid_size)] for _ in range(grid_size)]
                puzzle = WordSearchPuzzle.objects.create(
                    title=f"{category.name} Puzzle {i + 1}",
                    category=category,
                    level=WordSearchLevel.objects.get(level_number=random.choice([1, 2, 3])),
                    words=word_list,
                    grid_data=grid_data,
                    word_positions={},  # could be generated dynamically later
                    hints={w: f"Starts with {w[0].upper()}" for w in word_list},
                    is_active=True,
                )
        self.stdout.write(self.style.SUCCESS("✅ Created kid-friendly puzzles for each category"))

        self.stdout.write(self.style.SUCCESS("🎉 Kids’ Word Search data loaded successfully!"))
