from django.core.management.base import BaseCommand
from core.models import GameLevel, GameEmoji

class Command(BaseCommand):
    help = 'Populate game with initial data'

    def handle(self, *args, **kwargs):
        # Create game levels
        levels = [
            {'level_number': 1, 'rows': 1, 'columns': 4},
            {'level_number': 2, 'rows': 2, 'columns': 4},
            {'level_number': 3, 'rows': 3, 'columns': 4},
            {'level_number': 4, 'rows': 4, 'columns': 4},
            {'level_number': 5, 'rows': 5, 'columns': 4},
            {'level_number': 6, 'rows': 6, 'columns': 4},
        ]
        
        for level in levels:
            GameLevel.objects.get_or_create(**level)
        
        # Create emojis
        emojis = [
            {'emoji': '🍎', 'category': 'fruit'},
            {'emoji': '🍌', 'category': 'fruit'},
            {'emoji': '🍇', 'category': 'fruit'},
            {'emoji': '🍊', 'category': 'fruit'},
            {'emoji': '🍓', 'category': 'fruit'},
            {'emoji': '🍉', 'category': 'fruit'},
            {'emoji': '🍒', 'category': 'fruit'},
            {'emoji': '🍑', 'category': 'fruit'},
            {'emoji': '🥝', 'category': 'fruit'},
            {'emoji': '🍍', 'category': 'fruit'},
            {'emoji': '🥥', 'category': 'fruit'},
            {'emoji': '🥭', 'category': 'fruit'},
            {'emoji': '🍆', 'category': 'vegetable'},
            {'emoji': '🥕', 'category': 'vegetable'},
            {'emoji': '🌽', 'category': 'vegetable'},
            {'emoji': '🥒', 'category': 'vegetable'},
            {'emoji': '🍕', 'category': 'food'},
            {'emoji': '🍔', 'category': 'food'},
            {'emoji': '🌮', 'category': 'food'},
            {'emoji': '🍟', 'category': 'food'},
            {'emoji': '🍿', 'category': 'food'},
            {'emoji': '🧁', 'category': 'dessert'},
            {'emoji': '🍰', 'category': 'dessert'},
            {'emoji': '🎂', 'category': 'dessert'},
        ]
        
        for emoji_data in emojis:
            GameEmoji.objects.get_or_create(**emoji_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated game data!'))