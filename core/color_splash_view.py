from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
from .models import ColorSplashLevel, FruitColor, ColorPalette, ColorSplashSession, UserColorProgress
from .game_utils import get_age_from_birthdate, get_difficulty_by_age

def color_splash_game(request):
    """Render the Color Splash game page"""
    return render(request, 'color_splash/game.html')

@require_http_methods(["GET"])
def get_color_level_data(request):
    """Generate level data for Color Splash game, adjusted for user age"""
    level = int(request.GET.get('level', 1))
    
    # Get user age for difficulty adjustment
    user = request.user if request.user.is_authenticated else None
    user_age = None
    if user and hasattr(user, 'profile') and user.profile.date_of_birth:
        user_age = get_age_from_birthdate(user.profile.date_of_birth)
    
    try:
        level_config = ColorSplashLevel.objects.get(level_number=level)
        required_matches = level_config.required_matches
        grid_size = level_config.grid_size
        
        # Adjust difficulty based on user age (fewer matches and smaller grid for younger kids)
        if user_age is not None:
            if user_age <= 6:
                # Ages 3-6: Easier levels (max 4 matches, smaller grid)
                required_matches = min(required_matches, 4)
                grid_size = min(grid_size, 3)
            elif user_age <= 9:
                # Ages 7-9: Medium levels (max 6 matches, medium grid)
                required_matches = min(required_matches, 6)
                grid_size = min(grid_size, 4)
            # Ages 10+: Keep original difficulty
    except ColorSplashLevel.DoesNotExist:
        # Fallback configuration with age adjustment
        required_matches = min(4, 2 + level)
        grid_size = 3 if user_age and user_age <= 6 else 4
        
        if user_age is not None:
            if user_age <= 6:
                required_matches = min(required_matches, 4)
                grid_size = min(grid_size, 3)
            elif user_age <= 9:
                required_matches = min(required_matches, 6)
                grid_size = min(grid_size, 4)
    
    # Get active fruits
    active_fruits = list(FruitColor.objects.filter(is_active=True))
    
    if len(active_fruits) < required_matches:
        return JsonResponse({
            'error': 'Not enough fruits in database'
        }, status=400)
    
    # Select random fruits for this level
    selected_fruits = random.sample(active_fruits, required_matches)
    
    # Prepare fruit data
    fruits_data = [
        {
            'id': fruit.id,
            'name': fruit.name,
            'emoji': fruit.emoji,
            'color': fruit.color,
            'hex_color': fruit.hex_color
        }
        for fruit in selected_fruits
    ]
    
    # Get available colors from palette
    colors = list(ColorPalette.objects.filter(is_active=True).values('name', 'hex_code'))
    
    return JsonResponse({
        'level': level,
        'required_matches': required_matches,
        'grid_size': grid_size,
        'fruits': fruits_data,
        'colors': colors
    })

@csrf_exempt
@require_http_methods(["POST"])
def save_color_game_state(request):
    """Save Color Splash game state"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level', 1)
        score = data.get('score', 0)
        matched_count = data.get('matched_count', 0)
        time_elapsed = data.get('time_elapsed', 0)
        game_data = data.get('game_data', {})
        
        # Create or update game session
        session, created = ColorSplashSession.objects.update_or_create(
            session_id=session_id,
            defaults={
                'level': level,
                'score': score,
                'matched_count': matched_count,
                'time_elapsed': time_elapsed,
                'game_data': game_data,
                'is_active': True
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def load_color_game_state(request):
    """Load Color Splash game state"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            session = ColorSplashSession.objects.get(
                session_id=session_id,
                is_active=True
            )
            return JsonResponse({
                'status': 'success',
                'level': session.level,
                'score': session.score,
                'matched_count': session.matched_count,
                'time_elapsed': session.time_elapsed,
                'game_data': session.game_data
            })
        except ColorSplashSession.DoesNotExist:
            return JsonResponse({
                'status': 'not_found'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'No session ID provided'
    }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def complete_color_level(request):
    """Handle Color Splash level completion"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level', 1)
        score = data.get('score', 0)
        perfect = data.get('perfect', False)
        
        # Update user progress if authenticated
        if request.user.is_authenticated:
            progress, created = UserColorProgress.objects.get_or_create(
                user=request.user,
                defaults={'highest_level': level}
            )
            
            if level > progress.highest_level:
                progress.highest_level = level
            
            progress.total_score += score
            progress.games_played += 1
            
            if perfect:
                progress.perfect_matches += 1
            
            progress.save()
        
        # Deactivate session
        ColorSplashSession.objects.filter(
            session_id=session_id
        ).update(is_active=False)
        
        return JsonResponse({
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)