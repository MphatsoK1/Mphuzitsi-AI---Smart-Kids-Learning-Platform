from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
import logging
import random
import uuid
from .forms import *
from .models import *

logger = logging.getLogger(__name__)

def splash_screen(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'splash_screen.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import random
import json

# ============================================
# WORD CAPTURE GAME VIEWS
# ============================================

def capture_words(request):
    """Main word capture game view"""
    return render(request, 'capture_words.html')


@require_http_methods(["GET"])
def get_capture_words(request):
    """API endpoint to get words for Word Capture game"""
    pos_type = request.GET.get('type', 'noun')
    difficulty = request.GET.get('difficulty', 'easy')
    count = int(request.GET.get('count', 8))
    
    try:
        # Get part of speech
        pos = CapturePartOfSpeech.objects.filter(name=pos_type).first()
        
        if not pos:
            return JsonResponse({
                'error': f'Part of speech "{pos_type}" not found'
            }, status=404)
        
        # Get words for this type and difficulty
        words = list(CaptureWord.objects.filter(
            part_of_speech=pos,
            difficulty=difficulty
        ))
        
        # If not enough words, get from easier difficulties
        if len(words) < count:
            if difficulty == 'hard':
                words += list(CaptureWord.objects.filter(
                    part_of_speech=pos,
                    difficulty='medium'
                ))
            if difficulty in ['hard', 'medium']:
                words += list(CaptureWord.objects.filter(
                    part_of_speech=pos,
                    difficulty='easy'
                ))
        
        if len(words) < count:
            return JsonResponse({
                'error': f'Not enough words available (need {count}, have {len(words)})'
            }, status=404)
        
        # Random selection
        selected_words = random.sample(words, min(count, len(words)))
        
        return JsonResponse({
            'words': [w.word.upper() for w in selected_words],
            'hints': {w.word.upper(): w.hint for w in selected_words if w.hint},
            'type': pos_type,
            'difficulty': difficulty,
            'description': pos.description,
            'hint_text': pos.hint_text
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_mixed_capture_words(request):
    """Get a mix of different parts of speech for Word Capture"""
    difficulty = request.GET.get('difficulty', 'easy')
    target_type = request.GET.get('target', 'noun')
    target_count = int(request.GET.get('target_count', 5))
    other_count = int(request.GET.get('other_count', 3))
    
    try:
        # Get target words
        target_pos = CapturePartOfSpeech.objects.filter(name=target_type).first()
        if not target_pos:
            return JsonResponse({'error': 'Target type not found'}, status=404)
        
        target_words = list(CaptureWord.objects.filter(
            part_of_speech=target_pos,
            difficulty=difficulty
        ))
        
        # Fallback to easier difficulties if needed
        if len(target_words) < target_count:
            if difficulty == 'hard':
                target_words += list(CaptureWord.objects.filter(
                    part_of_speech=target_pos,
                    difficulty='medium'
                ))
            if difficulty in ['hard', 'medium']:
                target_words += list(CaptureWord.objects.filter(
                    part_of_speech=target_pos,
                    difficulty='easy'
                ))
        
        if len(target_words) < target_count:
            return JsonResponse({'error': 'Not enough target words'}, status=404)
        
        selected_targets = random.sample(target_words, target_count)
        
        # Get other words (different parts of speech)
        other_types = CapturePartOfSpeech.objects.exclude(name=target_type)
        other_words = []
        
        for pos in other_types:
            words = list(CaptureWord.objects.filter(
                part_of_speech=pos,
                difficulty=difficulty
            ))
            
            # Fallback to easier difficulties
            if len(words) < 2:
                if difficulty == 'hard':
                    words += list(CaptureWord.objects.filter(
                        part_of_speech=pos,
                        difficulty='medium'
                    ))
                if difficulty in ['hard', 'medium']:
                    words += list(CaptureWord.objects.filter(
                        part_of_speech=pos,
                        difficulty='easy'
                    ))
            
            if words:
                count = max(1, other_count // len(other_types))
                other_words.extend(random.sample(words, min(count, len(words))))
        
        # Shuffle all words together
        all_words = selected_targets + other_words[:other_count]
        random.shuffle(all_words)
        
        return JsonResponse({
            'all_words': [w.word.upper() for w in all_words],
            'target_words': [w.word.upper() for w in selected_targets],
            'word_types': {w.word.upper(): w.part_of_speech.name for w in all_words},
            'hints': {w.word.upper(): w.hint for w in all_words if w.hint},
            'target_type': target_type,
            'difficulty': difficulty,
            'description': target_pos.description,
            'hint_text': target_pos.hint_text
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_capture_session(request):
    """Save Word Capture game session data"""
    try:
        data = json.loads(request.body)
        
        session = CaptureGameSession.objects.create(
            player_name=data.get('player_name', 'Player'),
            score=data.get('score', 0),
            level_reached=data.get('level', 1),
            rounds_completed=data.get('rounds', 0),
            words_captured=data.get('words_captured', 0),
            time_spent=data.get('time_spent', 0),
            completed=data.get('completed', False)
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'rank': get_capture_player_rank(session.score)
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_capture_leaderboard(request):
    """Get top players for Word Capture game"""
    limit = int(request.GET.get('limit', 10))
    
    top_sessions = CaptureGameSession.objects.all()[:limit]
    
    leaderboard = [{
        'rank': idx + 1,
        'player_name': session.player_name,
        'score': session.score,
        'level': session.level_reached,
        'rounds': session.rounds_completed,
        'words_captured': session.words_captured,
        'date': session.created_at.strftime('%Y-%m-%d')
    } for idx, session in enumerate(top_sessions)]
    
    return JsonResponse({'leaderboard': leaderboard})


def get_capture_player_rank(score):
    """Get player's rank in Word Capture based on score"""
    higher_scores = CaptureGameSession.objects.filter(score__gt=score).count()
    return higher_scores + 1


# ============================================
# WORD SEARCH GAME VIEWS
# ============================================

import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import WordSearchLevel, WordSearchCategory, WordSearchPuzzle, WordSearchGameSession, UserWordSearchProgress

def words_search(request):
    """Main word search game view"""
    return render(request, 'words_search.html')

def generate_word_search_puzzle(level_number):
    """Generate a word search puzzle for the given level"""
    try:
        level = WordSearchLevel.objects.get(level_number=level_number)
        
        # Get active categories
        categories = WordSearchCategory.objects.filter(is_active=True)
        if not categories.exists():
            return None
        
        # Pick a random category
        category = random.choice(categories)
        
        # Get puzzles for this level and category
        puzzles = WordSearchPuzzle.objects.filter(
            level=level,
            category=category,
            is_active=True
        )
        
        if puzzles.exists():
            # Use pre-generated puzzle
            puzzle = random.choice(puzzles)
            return {
                'words': puzzle.words,
                'grid_data': puzzle.grid_data,
                'word_positions': puzzle.word_positions,
                'hints': puzzle.hints,
                'category': category.name,
                'title': puzzle.title,
                'grid_size': level.grid_size,
                'time_limit': level.time_limit
            }
        else:
            # Generate puzzle on the fly
            words = generate_words_for_level(level, category)
            if not words:
                return None
            
            grid_data, word_positions = generate_grid_data(words, level.grid_size)
            
            return {
                'words': words,
                'grid_data': grid_data,
                'word_positions': word_positions,
                'hints': generate_hints(words),
                'category': category.name,
                'title': f"{category.name} Challenge",
                'grid_size': level.grid_size,
                'time_limit': level.time_limit
            }
            
    except WordSearchLevel.DoesNotExist:
        return None

def generate_words_for_level(level, category):
    """Generate appropriate words for the level and category"""
    # This would be enhanced with actual word databases
    word_lists = {
        'easy': ['CAT', 'DOG', 'SUN', 'MOON', 'STAR', 'FISH', 'BIRD', 'TREE', 'BOOK', 'BALL'],
        'medium': ['APPLE', 'GRAPE', 'TIGER', 'ZEBRA', 'HAPPY', 'SMILE', 'OCEAN', 'RIVER', 'PIZZA', 'BREAD'],
        'hard': ['DRAGON', 'CASTLE', 'ROCKET', 'PLANET', 'JUNGLE', 'FOREST', 'RAINBOW', 'DOLPHIN', 'PENGUIN', 'OCTOPUS'],
        'expert': ['ADVENTURE', 'DISCOVERY', 'MYSTERIOUS', 'TREASURE', 'EXPLORATION', 'CHALLENGE', 'VICTORY', 'CELEBRATION']
    }
    
    difficulty = level.difficulty
    word_count = level.word_count
    
    if difficulty in word_lists:
        words = word_lists[difficulty][:word_count]
        return [word.upper() for word in words]
    
    return []

def generate_grid_data(words, grid_size):
    """Generate grid data and word positions"""
    # Simplified grid generation - you can enhance this with proper algorithm
    grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
    word_positions = {}
    
    # Fill grid with random letters
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i][j] = random.choice(letters)
    
    # Place words (simplified - you'd want a proper algorithm)
    for word in words:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            row = random.randint(0, grid_size - 1)
            col = random.randint(0, grid_size - 1)
            
            if can_place_word(grid, word, row, col, direction, grid_size):
                positions = place_word(grid, word, row, col, direction)
                word_positions[word] = positions
                placed = True
            
            attempts += 1
    
    # Flatten grid for frontend
    flat_grid = []
    for row in grid:
        flat_grid.extend(row)
    
    return flat_grid, word_positions

def can_place_word(grid, word, row, col, direction, grid_size):
    """Check if a word can be placed at the given position"""
    word_len = len(word)
    
    if direction == 'horizontal':
        if col + word_len > grid_size:
            return False
        for i in range(word_len):
            if grid[row][col + i] != '' and grid[row][col + i] != word[i]:
                return False
    elif direction == 'vertical':
        if row + word_len > grid_size:
            return False
        for i in range(word_len):
            if grid[row + i][col] != '' and grid[row + i][col] != word[i]:
                return False
    elif direction == 'diagonal':
        if row + word_len > grid_size or col + word_len > grid_size:
            return False
        for i in range(word_len):
            if grid[row + i][col + i] != '' and grid[row + i][col + i] != word[i]:
                return False
    
    return True

def place_word(grid, word, row, col, direction):
    """Place a word in the grid and return its positions"""
    positions = []
    word_len = len(word)
    
    if direction == 'horizontal':
        for i in range(word_len):
            grid[row][col + i] = word[i]
            positions.append(row * len(grid) + (col + i))
    elif direction == 'vertical':
        for i in range(word_len):
            grid[row + i][col] = word[i]
            positions.append((row + i) * len(grid) + col)
    elif direction == 'diagonal':
        for i in range(word_len):
            grid[row + i][col + i] = word[i]
            positions.append((row + i) * len(grid) + (col + i))
    
    return positions

def generate_hints(words):
    """Generate hints for words"""
    hints = {}
    for word in words:
        hints[word] = f"A word with {len(word)} letters"
    return hints

def get_word_search_level(request):
    """Get word search puzzle for a specific level"""
    level_number = int(request.GET.get('level', 1))
    
    puzzle_data = generate_word_search_puzzle(level_number)
    
    if not puzzle_data:
        return JsonResponse({'error': 'Could not generate puzzle'}, status=404)
    
    return JsonResponse({
        'level_number': level_number,
        'words': puzzle_data['words'],
        'grid_data': puzzle_data['grid_data'],
        'word_positions': puzzle_data['word_positions'],
        'hints': puzzle_data['hints'],
        'category': puzzle_data['category'],
        'title': puzzle_data['title'],
        'grid_size': puzzle_data['grid_size'],
        'time_limit': puzzle_data['time_limit']
    })

@csrf_exempt
@require_http_methods(["POST"])
def start_word_search_session(request):
    """Start a new word search game session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        player_name = data.get('player_name', 'Player')
        
        user = request.user if request.user.is_authenticated else None
        
        session = WordSearchGameSession.objects.create(
            session_id=session_id,
            player_name=player_name,
            user=user,
            current_level=1,
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.session_id,
            'message': 'Word Search game session started'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_word_search_progress(request):
    """Update word search game progress"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level')
        score = data.get('score')
        words_found = data.get('words_found')
        total_words = data.get('total_words')
        hints_used = data.get('hints_used', 0)
        time_spent = data.get('time_spent')
        perfect_puzzle = data.get('perfect_puzzle', False)
        
        session = WordSearchGameSession.objects.get(session_id=session_id)
        session.current_level = level
        session.total_score = score
        session.words_found = words_found
        session.total_words = total_words
        session.hints_used = hints_used
        session.time_spent = time_spent
        if perfect_puzzle:
            session.perfect_puzzles += 1
        session.save()
        
        # Update user progress if authenticated
        if session.user:
            progress, created = UserWordSearchProgress.objects.get_or_create(
                user=session.user
            )
            if level > progress.highest_level:
                progress.highest_level = level
            progress.total_score += score
            progress.total_words_found += words_found
            if perfect_puzzle:
                progress.perfect_puzzles += 1
            progress.games_played += 1
            progress.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_next_word_search_level(request):
    """Get next word search level information"""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1
    
    try:
        level = WordSearchLevel.objects.get(level_number=next_level)
        return JsonResponse({
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'unlock_score': level.unlock_score
        })
    except WordSearchLevel.DoesNotExist:
        return JsonResponse({'error': 'No more levels'}, status=404)

# @require_http_methods(["GET"])
# def get_search_leaderboard(request):
#     """Get top 10 game sessions for Word Search"""
#     top_sessions = SearchGameSession.objects.all().order_by('-score')[:10]
    
#     leaderboard = [{
#         'rank': idx + 1,
#         'player_name': session.player_name,
#         'score': session.score,
#         'level': session.level_reached,
#         'words_found': session.words_found
#     } for idx, session in enumerate(top_sessions)]
    
#     return JsonResponse({'leaderboard': leaderboard})


def tracing_letters(request):
    return render(request, 'tracing_letters.html')



def match_game(request):
    return render(request, 'match_game.html')

def artificial_intelligence(request):
    return render(request, 'artificial_intelligence.html')

def games_page(request):
    return render(request, 'games_page.html')

def word_search_game(request, category_id=None):
    return render(request, 'learning/word_search.html')

# @csrf_exempt
# @require_http_methods(["POST"])
# def new_word_search_game(request):
#     try:
#         data = json.loads(request.body)
#         category_id = data.get('category_id')
#         grid_size = min(max(data.get('grid_size', 10), 6), 20)
#         allow_crossing = data.get('allow_crossing', True)
#         difficulty = data.get('difficulty', 'medium')
#         learning_mode = data.get('learning_mode', 'vocabulary')
        
#         category = None
#         if category_id:
#             try:
#                 category = WordCategory.objects.get(id=category_id, is_active=True)
#             except WordCategory.DoesNotExist:
#                 pass
        
#         game = WordSearchGame(
#             grid_size=grid_size,
#             difficulty=difficulty,
#             learning_mode=learning_mode,
#             category=category
#         )
        
#         grid, placed_words = game.generate_grid(allow_crossing=allow_crossing)
        
#         session_id = request.session.session_key or str(timezone.now().timestamp())
#         if not request.session.session_key:
#             request.session.create()
#             session_id = request.session.session_key
        
#         game_session = WordSearchGameSession.objects.create(
#             game=game,
#             session_id=session_id,
#             found_words=[]
#         )
        
#         word_details = {}
#         for word_info in placed_words:
#             word = word_info['word']
#             try:
#                 word_item = WordItem.objects.get(word__iexact=word, is_active=True)
#                 word_details[word] = {
#                     'definition': word_item.definition,
#                     'part_of_speech': word_item.part_of_speech,
#                     'phonetic': word_item.phonetic_spelling,
#                     'example': word_item.example_sentence,
#                     'image': word_item.image.url if word_item.image else None,
#                     'audio': word_item.audio.url if word_item.audio else None
#                 }
#             except WordItem.DoesNotExist:
#                 word_details[word] = {
#                     'definition': f"A word meaning {word.lower()}",
#                     'part_of_speech': 'noun',
#                     'phonetic': '',
#                     'example': f"I like the word {word}.",
#                     'image': None,
#                     'audio': None
#                 }
        
#         return JsonResponse({
#             'game_id': game.id,
#             'session_id': game_session.id,
#             'grid': grid,
#             'words': [w['word'] for w in placed_words],
#             'placed_words': placed_words,
#             'word_details': word_details,
#             'grid_size': grid_size,
#             'difficulty': difficulty,
#             'learning_mode': learning_mode,
#             'category': category.name if category else 'General'
#         })
    
#     except Exception as e:
#         logger.error(f"Error creating new word search game: {str(e)}")
#         return JsonResponse({'error': 'Failed to create game'}, status=500)

# @csrf_exempt
# @require_http_methods(["POST"])
# def check_word_search_word(request, game_id):
#     try:
#         game = WordSearchGame.objects.get(id=game_id)
#         data = json.loads(request.body)
#         selected_positions = data.get('positions', [])
#         session_id = data.get('session_id')
#         user_identifier = data.get('user_identifier')
        
#         if not selected_positions:
#             return JsonResponse({'valid': False, 'message': 'No positions selected'})
        
#         grid_size = game.grid_size
#         for pos in selected_positions:
#             if not (0 <= pos[0] < grid_size and 0 <= pos[1] < grid_size):
#                 return JsonResponse({'valid': False, 'message': 'Invalid positions'})
        
#         selected_set = set(tuple(pos) for pos in selected_positions)
        
#         direction = game.validate_word_positions(selected_positions)
#         if not direction:
#             return JsonResponse({
#                 'valid': False, 
#                 'message': 'Positions must form a straight line'
#             })
        
#         for word_info in game.words_data:
#             word_positions = set(tuple(pos) for pos in word_info['positions'])
#             if selected_set == word_positions:
#                 word = word_info['word']
                
#                 if session_id:
#                     try:
#                         game_session = WordSearchGameSession.objects.get(id=session_id, game=game)
#                         if word not in game_session.found_words:
#                             game_session.found_words.append(word)
#                             game_session.score += len(word) * 10
#                             game_session.save()
                            
#                             if user_identifier:
#                                 try:
#                                     word_item = WordItem.objects.get(word__iexact=word)
#                                     progress, created = UserWordProgress.objects.get_or_create(
#                                         user_identifier=user_identifier,
#                                         word=word_item,
#                                         defaults={'times_correct': 1, 'times_attempted': 1}
#                                     )
#                                     if not created:
#                                         progress.times_correct += 1
#                                         progress.times_attempted += 1
#                                         progress.save()
#                                 except WordItem.DoesNotExist:
#                                     pass
                            
#                             if len(game_session.found_words) == len(game.words_data):
#                                 game_session.completed = True
#                                 game_session.end_time = timezone.now()
#                                 game_session.save()
#                                 game.completed = True
#                                 game.save()
#                     except WordSearchGameSession.DoesNotExist:
#                         pass
                
#                 positive_messages = [
#                     "Excellent! 🎉", "Bravo! 👏", "Marvelous! ✨", "Outstanding! 🌟",
#                     "Fantastic! 🚀", "Wonderful! 💫", "Superb! 🔥", "Terrific! ⭐",
#                     "Perfect! ✅", "Awesome! 😎", "Brilliant! 💎", "Amazing! 🌈"
#                 ]
                
#                 return JsonResponse({
#                     'valid': True,
#                     'word': word,
#                     'direction': direction,
#                     'message': random.choice(positive_messages),
#                     'positions': word_info['positions']
#                 })
        
#         negative_messages = [
#             "Try again! 🔄", "Not quite! 🤔", "Keep trying! 💪", "Almost! 📍",
#             "Look carefully! 👀", "You can do it! 🌟", "Nice try! 👍", "Next time! ⏭️"
#         ]
        
#         return JsonResponse({
#             'valid': False, 
#             'message': random.choice(negative_messages)
#         })
        
#     except WordSearchGame.DoesNotExist:
#         return JsonResponse({'error': 'Game not found'}, status=404)
#     except Exception as e:
#         logger.error(f"Error checking word: {str(e)}")
#         return JsonResponse({'error': 'Server error'}, status=500)

# @csrf_exempt
# @require_http_methods(["POST"])
# def use_word_search_hint(request, game_id):
#     try:
#         game = WordSearchGame.objects.get(id=game_id)
#         data = json.loads(request.body)
#         session_id = data.get('session_id')
        
#         if not session_id:
#             return JsonResponse({'error': 'Session ID required'}, status=400)
        
#         game_session = WordSearchGameSession.objects.get(id=session_id, game=game)
        
#         found_words = set(game_session.found_words)
#         unfound_words = [w for w in game.words_data if w['word'] not in found_words]
        
#         if not unfound_words:
#             return JsonResponse({'error': 'All words already found'}, status=400)
        
#         game_session.hints_used += 1
#         game_session.save()
        
#         hint_word = random.choice(unfound_words)
        
#         return JsonResponse({
#             'hint_word': hint_word['word'],
#             'hint_positions': hint_word['positions'],
#             'hint_direction': hint_word['direction'],
#             'hints_used': game_session.hints_used
#         })
        
#     except (WordSearchGame.DoesNotExist, WordSearchGameSession.DoesNotExist):
#         return JsonResponse({'error': 'Game or session not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_word_categories(request):
#     categories = WordCategory.objects.filter(is_active=True)
#     data = [
#         {
#             'id': category.id,
#             'name': category.name,
#             'icon': category.icon,
#             'description': category.description,
#             'word_count': category.words.filter(is_active=True).count()
#         }
#         for category in categories
#     ]
#     return JsonResponse({'categories': data})

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_user_word_progress(request, user_identifier):
#     progress = UserWordProgress.objects.filter(user_identifier=user_identifier)
#     data = [
#         {
#             'word': item.word.word,
#             'category': item.word.category.name,
#             'times_correct': item.times_correct,
#             'times_attempted': item.times_attempted,
#             'accuracy': item.accuracy,
#             'last_played': item.last_played.isoformat()
#         }
#         for item in progress
#     ]
#     return JsonResponse({'progress': data})

# @csrf_exempt
# @require_http_methods(["GET"])
# def word_search_leaderboard(request):
#     completed_sessions = WordSearchGameSession.objects.filter(
#         completed=True
#     ).select_related('game').order_by('-score', 'end_time')[:10]
    
#     leaderboard_data = [
#         {
#             'session_id': session.session_id[:8] + '...',
#             'score': session.score,
#             'completion_time': session.end_time.isoformat() if session.end_time else None,
#             'difficulty': session.game.difficulty,
#             'learning_mode': session.game.learning_mode,
#             'words_found': len(session.found_words)
#         }
#         for session in completed_sessions
#     ]
    
#     return JsonResponse({'leaderboard': leaderboard_data})

# def game_one(request):
#     return render(request, 'game_one.html')

# def index_view(request):
#     return render(request, 'learning/index.html')

# def game_page(request, category_id):
#     return render(request, 'learning/game.html')

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_categories(request):
#     categories = Category.objects.filter(is_active=True)
#     data = [
#         {
#             'id': category.id,
#             'name': category.name,
#             'type': category.category_type,
#             'icon': category.icon,
#             'description': category.description
#         }
#         for category in categories
#     ]
#     return JsonResponse({'categories': data})

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_category_task_sets(request, category_id):
#     try:
#         category = Category.objects.get(id=category_id, is_active=True)
#         task_sets = category.task_sets.filter(is_active=True)
        
#         data = [
#             {
#                 'id': task_set.id,
#                 'name': task_set.name,
#                 'description': task_set.description,
#                 'items_per_set': task_set.items_per_set
#             }
#             for task_set in task_sets
#         ]
        
#         return JsonResponse({
#             'category': category.name,
#             'task_sets': data
#         })
    
#     except Category.DoesNotExist:
#         return JsonResponse({'error': 'Category not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_task_set_items(request, task_set_id):
#     try:
#         task_set = TaskSet.objects.get(id=task_set_id, is_active=True)
#         category = task_set.category
        
#         if category.category_type == 'phonics':
#             items = list(PhonicsItem.objects.filter(is_active=True))
#             if len(items) > task_set.items_per_set:
#                 items = random.sample(items, task_set.items_per_set)
            
#             data = [
#                 {
#                     'id': f"phonics_{item.id}",
#                     'letter': item.letter,
#                     'words': item.words,
#                     'audio': item.audio.url if item.audio else None,
#                     'image': item.image.url if item.image else None
#                 }
#                 for item in items
#             ]
#         else:
#             items = task_set.get_random_items()
#             data = [
#                 {
#                     'id': item.id,
#                     'name': item.name,
#                     'image': item.image.url if item.image else None,
#                     'color': item.color_code,
#                     'display_text': item.display_text,
#                     'audio': item.audio.url if item.audio else None
#                 }
#                 for item in items
#             ]
        
#         return JsonResponse({
#             'task_set': task_set.name,
#             'category': category.name,
#             'category_type': category.category_type,
#             'items': data
#         })
    
#     except TaskSet.DoesNotExist:
#         return JsonResponse({'error': 'Task set not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["POST"])
# def start_game_session(request):
#     try:
#         data = json.loads(request.body)
#         task_set_id = data.get('task_set_id')
#         time_limit = data.get('time_limit', 120)
        
#         task_set = TaskSet.objects.get(id=task_set_id)
#         session_id = str(uuid.uuid4())
        
#         session = MatchingGameSession.objects.create(
#             session_id=session_id,
#             category=task_set.category,
#             total_items=task_set.items_per_set
#         )
        
#         return JsonResponse({
#             'session_id': session_id,
#             'category': task_set.category.name,
#             'task_set': task_set.name,
#             'total_items': task_set.items_per_set,
#             'time_limit': time_limit
#         })
    
#     except TaskSet.DoesNotExist:
#         return JsonResponse({'error': 'Task set not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

# @csrf_exempt
# @require_http_methods(["POST"])
# def update_game_progress(request):
#     try:
#         data = json.loads(request.body)
#         session_id = data.get('session_id')
#         score = data.get('score', 0)
#         completed = data.get('completed', False)
#         time_taken = data.get('time_taken', 0)
        
#         session = MatchingGameSession.objects.get(session_id=session_id)
#         session.score = score
#         session.completed = completed
#         session.time_taken = time_taken
#         session.save()
        
#         return JsonResponse({'status': 'success'})
    
#     except MatchingGameSession.DoesNotExist:
#         return JsonResponse({'error': 'Session not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["POST"])
# def save_user_progress(request):
#     try:
#         data = json.loads(request.body)
#         user_identifier = data.get('user_identifier')
#         category_id = data.get('category_id')
#         items_completed = data.get('items_completed', [])
#         total_score = data.get('total_score', 0)
#         level_completed = data.get('level_completed', False)
        
#         category = Category.objects.get(id=category_id)
        
#         progress, created = UserProgress.objects.get_or_create(
#             user_identifier=user_identifier,
#             category=category,
#             defaults={
#                 'items_completed': items_completed,
#                 'total_score': total_score,
#                 'games_played': 1,
#                 'levels_completed': 1 if level_completed else 0
#             }
#         )
        
#         if not created:
#             progress.items_completed = list(set(progress.items_completed + items_completed))
#             progress.total_score += total_score
#             progress.games_played += 1
#             if level_completed:
#                 progress.levels_completed += 1
#             progress.save()
        
#         return JsonResponse({'status': 'success'})
    
#     except Category.DoesNotExist:
#         return JsonResponse({'error': 'Category not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["GET"])
# def get_user_progress(request, user_identifier):
#     progress = UserProgress.objects.filter(user_identifier=user_identifier)
#     data = [
#         {
#             'category': p.category.name,
#             'category_id': p.category.id,
#             'items_completed': len(p.items_completed),
#             'total_score': p.total_score,
#             'games_played': p.games_played,
#             'levels_completed': p.levels_completed
#         }
#         for p in progress
#     ]
#     return JsonResponse({'progress': data})

# @csrf_exempt
# @require_http_methods(["GET"])
# def matching_leaderboard(request):
#     completed_sessions = MatchingGameSession.objects.filter(
#         completed=True
#     ).select_related('category').order_by('-score', 'time_taken')[:10]
    
#     leaderboard_data = [
#         {
#             'session_id': session.session_id[:8] + '...',
#             'score': session.score,
#             'completion_time': session.time_taken,
#             'category': session.category.name,
#             'items_completed': session.score // 10
#         }
#         for session in completed_sessions
#     ]
    
#     return JsonResponse({'leaderboard': leaderboard_data})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if not user.profile.profile_completed:
                    messages.info(request, 'Please complete your profile setup.')
                    return redirect('profile_setup')
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Registration successful! Welcome, {user.username}!')
            return redirect('profile_setup')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def profile_setup_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.profile_completed:
        return redirect('home')
    
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save()
            messages.success(request, 'Profile setup completed successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please select an avatar.')
    else:
        form = ProfileSetupForm(instance=profile, user=request.user)
    
    return render(request, 'choose_avatar.html', {
        'form': form,
        'user': request.user,
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def home_view(request):
    if not request.user.profile.profile_completed:
        return redirect('profile_setup')
    return render(request, 'homepage.html')

@login_required
def profile_view(request):
    user_stats = {
        'level': 1,
        'points': 0,
        'games_played': 0,
        'quizzes_taken': 0
    }
    
    # word_search_sessions = WordSearchGameSession.objects.filter(
    #     game__completed=True
    # ).count()
    
    # matching_sessions = MatchingGameSession.objects.filter(
    #     completed=True
    # ).count()
    
    # user_stats['games_played'] = word_search_sessions + matching_sessions
    
    # word_search_activities = WordSearchGameSession.objects.filter(
    #     game__completed=True
    # ).order_by('-end_time')[:5]
    
    # matching_activities = MatchingGameSession.objects.filter(
    #     completed=True
    # ).order_by('-updated_at')[:5]
    
    # recent_activities = [
    #     {
    #         'title': 'Completed Word Search Game',
    #         'timestamp': session.end_time,
    #         'score': f"{session.score} points",
    #         'color': 'blue',
    #         'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>'
    #     }
    #     for session in word_search_activities
    # ] + [
    #     {
    #         'title': f"Completed {session.category.name} Game",
    #         'timestamp': session.updated_at,
    #         'score': f"{session.score} points",
    #         'color': 'green',
    #         'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"/>'
    #     }
    #     for session in matching_activities
    # ]
    
    # recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    # recent_activities = recent_activities[:5]
    
    context = {
        'user_stats': user_stats,
        # 'recent_activities': recent_activities
    }
    
    return render(request, 'user_profile.html', context)