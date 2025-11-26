# populate_search_words_script.py
import os
import django

# ✅ Set up Django environment (adjust this path if necessary)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aphunzitsi_ai.settings')
django.setup()

from core.models import SearchWordCategory, SearchWord

def populate_search_words():
    easy_categories = [
        {'name': 'Animals', 'words': ['CAT', 'DOG', 'BEE', 'ANT', 'OWL', 'COW', 'PIG', 'FROG', 'LION', 'BEAR']},
        {'name': 'Colors', 'words': ['RED', 'BLUE', 'PINK', 'GOLD', 'GRAY', 'GREEN', 'BLACK', 'WHITE', 'ORANGE', 'PURPLE']},
        {'name': 'Toys', 'words': ['BALL', 'DOLL', 'KITE', 'BIKE', 'GAME', 'CAR', 'PUZZLE', 'TRAIN', 'TEDDY', 'YOYO']},
        {'name': 'Nature', 'words': ['SUN', 'MOON', 'STAR', 'TREE', 'LEAF', 'RAIN', 'ROCK', 'FLOWER', 'SEA', 'HILL']},
        {'name': 'Body Parts', 'words': ['EYE', 'EAR', 'ARM', 'LEG', 'TOE', 'NOSE', 'MOUTH', 'HAND', 'FOOT', 'FINGER']},
    ]

    medium_categories = [
        {'name': 'Fruits', 'words': ['APPLE', 'GRAPE', 'LEMON', 'MELON', 'BERRY', 'ORANGE', 'PEACH', 'PLUM', 'MANGO', 'CHERRY']},
        {'name': 'Wild Animals', 'words': ['TIGER', 'ZEBRA', 'PANDA', 'KOALA', 'EAGLE', 'LION', 'BEAR', 'WOLF', 'FOX', 'MONKEY']},
        {'name': 'Emotions', 'words': ['HAPPY', 'SMILE', 'LAUGH', 'DANCE', 'SING', 'CRY', 'ANGER', 'LOVE', 'JOY', 'SURPRISE']},
        {'name': 'Water Bodies', 'words': ['OCEAN', 'RIVER', 'LAKE', 'BEACH', 'WAVE', 'POND', 'FALL', 'BAY', 'SEA', 'STREAM']},
        {'name': 'Food', 'words': ['PIZZA', 'BREAD', 'SALAD', 'PASTA', 'RICE', 'CAKE', 'SOUP', 'EGG', 'FISH', 'CHEESE']},
    ]

    hard_categories = [
        {'name': 'Fantasy', 'words': ['DRAGON', 'CASTLE', 'WIZARD', 'KNIGHT', 'MAGIC', 'TROLL', 'FAIRY', 'ELF', 'GIANT', 'UNICORN']},
        {'name': 'Space', 'words': ['ROCKET', 'PLANET', 'GALAXY', 'COMET', 'ORBIT', 'ASTEROID', 'SATELLITE', 'STAR', 'SUN', 'MOON']},
        {'name': 'Geography', 'words': ['JUNGLE', 'FOREST', 'DESERT', 'MOUNTAIN', 'VALLEY', 'CANYON', 'PLAIN', 'RIVER', 'ISLAND', 'GLACIER']},
        {'name': 'Weather', 'words': ['RAINBOW', 'THUNDER', 'LIGHTNING', 'TORNADO', 'BREEZE', 'HURRICANE', 'SNOW', 'FOG', 'WIND', 'DRIZZLE']},
        {'name': 'Sea Creatures', 'words': ['DOLPHIN', 'PENGUIN', 'OCTOPUS', 'TURTLE', 'WHALE', 'SHARK', 'CRAB', 'LOBSTER', 'SEAHORSE', 'JELLYFISH']},
    ]

    all_categories = [
        ('easy', easy_categories),
        ('medium', medium_categories),
        ('hard', hard_categories),
    ]

    for difficulty, categories in all_categories:
        for cat_data in categories:
            category, created = SearchWordCategory.objects.get_or_create(
                name=cat_data['name'],
                difficulty=difficulty,
                defaults={'description': f'{cat_data["name"]} words for {difficulty} level'}
            )
            for word in cat_data['words']:
                SearchWord.objects.get_or_create(
                    word=word,
                    category=category,
                    defaults={'hint': f'Think of {cat_data["name"].lower()}'}
                )
            if created:
                print(f"🆕 Created category: {category.name} ({difficulty})")

    print("✅ Successfully populated Search Word Categories and Words!")

if __name__ == "__main__":
    populate_search_words()
