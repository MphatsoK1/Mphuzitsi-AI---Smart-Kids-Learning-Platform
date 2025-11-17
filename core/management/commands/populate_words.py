# management/commands/populate_words.py
from django.core.management.base import BaseCommand
from core.models import WordCategory, Word

class Command(BaseCommand):
    help = 'Populate database with initial word sets'

    def handle(self, *args, **kwargs):
        # Easy words for 3-6 years
        easy_categories = [
            {
                'name': 'Animals',
                'words': ['CAT', 'DOG', 'BEE', 'ANT', 'OWL']
            },
            {
                'name': 'Colors',
                'words': ['RED', 'BLUE', 'PINK', 'GOLD', 'GRAY']
            },
            {
                'name': 'Toys',
                'words': ['BALL', 'DOLL', 'KITE', 'BIKE', 'GAME']
            },
            {
                'name': 'Nature',
                'words': ['SUN', 'MOON', 'STAR', 'TREE', 'LEAF']
            },
            {
                'name': 'Body Parts',
                'words': ['EYE', 'EAR', 'ARM', 'LEG', 'TOE']
            }
        ]
        
        # Medium words for 7-9 years
        medium_categories = [
            {
                'name': 'Fruits',
                'words': ['APPLE', 'GRAPE', 'LEMON', 'MELON', 'BERRY']
            },
            {
                'name': 'Wild Animals',
                'words': ['TIGER', 'ZEBRA', 'PANDA', 'KOALA', 'EAGLE']
            },
            {
                'name': 'Emotions',
                'words': ['HAPPY', 'SMILE', 'LAUGH', 'DANCE', 'SING']
            },
            {
                'name': 'Water Bodies',
                'words': ['OCEAN', 'RIVER', 'LAKE', 'BEACH', 'WAVE']
            },
            {
                'name': 'Food',
                'words': ['PIZZA', 'BREAD', 'SALAD', 'PASTA', 'RICE']
            }
        ]
        
        # Hard words for 10-12 years
        hard_categories = [
            {
                'name': 'Fantasy',
                'words': ['DRAGON', 'CASTLE', 'WIZARD', 'KNIGHT', 'MAGIC']
            },
            {
                'name': 'Space',
                'words': ['ROCKET', 'PLANET', 'GALAXY', 'COMET', 'ORBIT']
            },
            {
                'name': 'Geography',
                'words': ['JUNGLE', 'FOREST', 'DESERT', 'MOUNTAIN', 'VALLEY']
            },
            {
                'name': 'Weather',
                'words': ['RAINBOW', 'THUNDER', 'LIGHTNING', 'TORNADO', 'BREEZE']
            },
            {
                'name': 'Sea Creatures',
                'words': ['DOLPHIN', 'PENGUIN', 'OCTOPUS', 'TURTLE', 'WHALE']
            }
        ]
        
        # Create categories and words
        for difficulty, categories in [
            ('easy', easy_categories),
            ('medium', medium_categories),
            ('hard', hard_categories)
        ]:
            for cat_data in categories:
                category, created = WordCategory.objects.get_or_create(
                    name=cat_data['name'],
                    difficulty=difficulty,
                    defaults={'description': f'{cat_data["name"]} words for {difficulty} level'}
                )
                
                for word in cat_data['words']:
                    Word.objects.get_or_create(
                        word=word,
                        category=category,
                        defaults={'hint': f'Think of {cat_data["name"].lower()}'}
                    )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created category: {category.name} ({difficulty})')
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated word database!'))
