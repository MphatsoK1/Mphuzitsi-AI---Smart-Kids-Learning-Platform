from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .models import GameLevel, GameEmoji, GameSession, UserGameProgress
from .game_utils import get_age_from_birthdate, get_difficulty_by_age

def memory_game(request):
    """Render the main game page"""
    # Clear any existing session when starting fresh
    if 'game_session_id' in request.session:
        del request.session['game_session_id']
    return render(request, 'memory_match/game.html')

def get_level_data(request):
    """Generate level data based on grid size using database models, filtered by user age"""
    level = int(request.GET.get('level', 1))
    
    # Get user age for difficulty adjustment
    user = request.user if request.user.is_authenticated else None
    user_age = None
    if user and hasattr(user, 'profile') and user.profile.date_of_birth:
        user_age = get_age_from_birthdate(user.profile.date_of_birth)
    
    try:
        # Try to get level configuration from database
        level_config = GameLevel.objects.get(level_number=level)
        rows = level_config.rows
        cols = level_config.columns
        
        # Adjust grid size based on user age (smaller grids for younger kids)
        if user_age is not None:
            if user_age <= 6:
                # Ages 3-6: Limit to smaller grids (max 2x4 or 4x4)
                max_grid_size = max(rows, cols)
                if max_grid_size > 4:
                    # Reduce grid size proportionally
                    rows = min(rows, 2)
                    cols = min(cols, 4)
            elif user_age <= 9:
                # Ages 7-9: Limit to medium grids (max 4x4 or 5x4)
                max_grid_size = max(rows, cols)
                if max_grid_size > 5:
                    rows = min(rows, 4)
                    cols = min(cols, 5)
            # Ages 10+: Keep original grid size
        
        total_cards = rows * cols
        pairs = total_cards // 2
    except GameLevel.DoesNotExist:
        # Fallback to default configuration with age adjustment
        grid_configs = {
            1: (1, 4),
            2: (2, 4),
            3: (3, 4),
            4: (4, 4),
            5: (5, 4),
            6: (6, 4)
        }
        rows, cols = grid_configs.get(level, (1, 4))
        
        # Adjust grid size based on user age
        if user_age is not None:
            if user_age <= 6:
                rows = min(rows, 2)
                cols = min(cols, 4)
            elif user_age <= 9:
                rows = min(rows, 4)
                cols = min(cols, 5)
        
        total_cards = rows * cols
        pairs = total_cards // 2
    
    # Get emojis from database
    available_emojis = GameEmoji.objects.filter(is_active=True)
    if available_emojis.exists():
        emoji_list = [emoji.emoji for emoji in available_emojis]
    else:
        # Fallback emojis if none in database
        emoji_list = ['🍎', '🍌', '🍇', '🍊', '🍓', '🍉', '🍒', '🍑', 
                     '🥝', '🍍', '🥥', '🥭', '🍆', '🥕', '🌽', '🥒',
                     '🍕', '🍔', '🌮', '🍟', '🍿', '🧁', '🍰', '🎂']
    
    # Select random emojis for this level
    selected_emojis = random.sample(emoji_list, min(pairs, len(emoji_list)))
    
    # Create pairs and shuffle
    cards = selected_emojis * 2
    random.shuffle(cards)
    
    return JsonResponse({
        'level': level,
        'rows': rows,
        'cols': cols,
        'cards': cards,
        'total_pairs': pairs
    })

@csrf_exempt
def save_game_state(request):
    """Save game state to database"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            level = data.get('level', 1)
            moves = data.get('moves', 0)
            matched_pairs = data.get('matched_pairs', 0)
            cards_data = data.get('cards_data', {})
            
            # Create or update game session
            game_session, created = GameSession.objects.update_or_create(
                session_id=session_id,
                defaults={
                    'level': level,
                    'moves': moves,
                    'matched_pairs': matched_pairs,
                    'cards_data': cards_data,
                    'is_active': True
                }
            )
            
            return JsonResponse({'status': 'success', 'session_id': session_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

def load_game_state(request):
    """Load game state from database"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            game_session = GameSession.objects.get(session_id=session_id, is_active=True)
            return JsonResponse({
                'status': 'success',
                'level': game_session.level,
                'moves': game_session.moves,
                'matched_pairs': game_session.matched_pairs,
                'cards_data': game_session.cards_data
            })
        except GameSession.DoesNotExist:
            return JsonResponse({'status': 'not_found'})
    
    return JsonResponse({'status': 'error', 'message': 'No session ID provided'})

@csrf_exempt
def complete_level(request):
    """Handle level completion and update user progress"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            level = data.get('level', 1)
            moves = data.get('moves', 0)
            
            # Update user progress if user is authenticated
            if request.user.is_authenticated:
                progress, created = UserGameProgress.objects.get_or_create(
                    user=request.user,
                    defaults={'highest_level': level}
                )
                if level > progress.highest_level:
                    progress.highest_level = level
                progress.total_moves += moves
                progress.games_completed += 1
                progress.save()
            
            # Deactivate the game session
            GameSession.objects.filter(session_id=session_id).update(is_active=False)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})