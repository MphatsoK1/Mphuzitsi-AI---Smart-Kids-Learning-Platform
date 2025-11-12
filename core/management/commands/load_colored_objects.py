# management/commands/populate_color_splash.py

from django.core.management.base import BaseCommand
from core.models import ColorSplashLevel, FruitColor, ColorPalette

class Command(BaseCommand):
    help = 'Populate Color Splash game with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating Color Splash game data...')
        
        # Create levels
        levels_data = [
            {'level_number': 1, 'grid_size': 2, 'required_matches': 4, 'time_limit': 180},
            {'level_number': 2, 'grid_size': 2, 'required_matches': 4, 'time_limit': 150},
            {'level_number': 3, 'grid_size': 3, 'required_matches': 6, 'time_limit': 180},
            {'level_number': 4, 'grid_size': 3, 'required_matches': 6, 'time_limit': 150},
        ]
        
        for level in levels_data:
            obj, created = ColorSplashLevel.objects.get_or_create(**level)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {obj}'))
        
        # Create fruits with their colors
        fruits_data = [
            {'name': 'Apple', 'emoji': '🍎', 'color': 'Red', 'hex_color': '#DC2626'},
            {'name': 'Banana', 'emoji': '🍌', 'color': 'Yellow', 'hex_color': '#EAB308'},
            {'name': 'Grapes', 'emoji': '🍇', 'color': 'Purple', 'hex_color': '#9333EA'},
            {'name': 'Orange', 'emoji': '🍊', 'color': 'Orange', 'hex_color': '#F97316'},
            {'name': 'Strawberry', 'emoji': '🍓', 'color': 'Red', 'hex_color': '#DC2626'},
            {'name': 'Watermelon', 'emoji': '🍉', 'color': 'Green', 'hex_color': '#16A34A'},
            {'name': 'Cherries', 'emoji': '🍒', 'color': 'Red', 'hex_color': '#DC2626'},
            {'name': 'Peach', 'emoji': '🍑', 'color': 'Orange', 'hex_color': '#F97316'},
            {'name': 'Kiwi', 'emoji': '🥝', 'color': 'Green', 'hex_color': '#16A34A'},
            {'name': 'Pineapple', 'emoji': '🍍', 'color': 'Yellow', 'hex_color': '#EAB308'},
            {'name': 'Coconut', 'emoji': '🥥', 'color': 'Grey', 'hex_color': '#6B7280'},
            {'name': 'Mango', 'emoji': '🥭', 'color': 'Orange', 'hex_color': '#F97316'},
        ]
        
        for fruit in fruits_data:
            obj, created = FruitColor.objects.get_or_create(
                name=fruit['name'],
                defaults=fruit
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created fruit: {obj}'))
        
        # Create color palette
        colors_data = [
            {'name': 'Orange', 'hex_code': '#F97316', 'display_order': 1},
            {'name': 'Red', 'hex_code': '#DC2626', 'display_order': 2},
            {'name': 'Purple', 'hex_code': '#9333EA', 'display_order': 3},
            {'name': 'Yellow', 'hex_code': '#EAB308', 'display_order': 4},
            {'name': 'Green', 'hex_code': '#16A34A', 'display_order': 5},
            {'name': 'Grey', 'hex_code': '#6B7280', 'display_order': 6},
        ]
        
        for color in colors_data:
            obj, created = ColorPalette.objects.get_or_create(
                name=color['name'],
                defaults=color
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created color: {obj}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Successfully populated Color Splash data!'))


# Alternative: Quick shell commands
"""
Run in Django shell (python manage.py shell):

from your_app_name.models import ColorSplashLevel, FruitColor, ColorPalette

# Create levels
ColorSplashLevel.objects.create(level_number=1, grid_size=2, required_matches=4, time_limit=180)
ColorSplashLevel.objects.create(level_number=2, grid_size=2, required_matches=4, time_limit=150)
ColorSplashLevel.objects.create(level_number=3, grid_size=3, required_matches=6, time_limit=180)
ColorSplashLevel.objects.create(level_number=4, grid_size=3, required_matches=6, time_limit=150)

# Create fruits
FruitColor.objects.create(name='Apple', emoji='🍎', color='Red', hex_color='#DC2626')
FruitColor.objects.create(name='Banana', emoji='🍌', color='Yellow', hex_color='#EAB308')
FruitColor.objects.create(name='Grapes', emoji='🍇', color='Purple', hex_color='#9333EA')
FruitColor.objects.create(name='Orange', emoji='🍊', color='Orange', hex_color='#F97316')
FruitColor.objects.create(name='Strawberry', emoji='🍓', color='Red', hex_color='#DC2626')
FruitColor.objects.create(name='Watermelon', emoji='🍉', color='Green', hex_color='#16A34A')
FruitColor.objects.create(name='Cherries', emoji='🍒', color='Red', hex_color='#DC2626')
FruitColor.objects.create(name='Peach', emoji='🍑', color='Orange', hex_color='#F97316')

# Create color palette
ColorPalette.objects.create(name='Orange', hex_code='#F97316', display_order=1)
ColorPalette.objects.create(name='Red', hex_code='#DC2626', display_order=2)
ColorPalette.objects.create(name='Purple', hex_code='#9333EA', display_order=3)
ColorPalette.objects.create(name='Yellow', hex_code='#EAB308', display_order=4)
ColorPalette.objects.create(name='Green', hex_code='#16A34A', display_order=5)
ColorPalette.objects.create(name='Grey', hex_code='#6B7280', display_order=6)

print("✅ Data populated successfully!")
"""