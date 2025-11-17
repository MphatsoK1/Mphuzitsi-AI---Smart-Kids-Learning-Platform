from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
import json
import logging
import random
import uuid
from .forms import *
from .models import *
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age

logger = logging.getLogger(__name__)

def splash_screen(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'splash_screen.html')

# ============================================
# WORD CAPTURE GAME VIEWS
# ============================================

def capture_words(request):
    """Main word capture game view"""
    return render(request, 'capture_words.html')


@require_http_methods(["GET"])
def get_capture_words(request):
    """API endpoint to get words for Word Capture game, filtered by user age"""
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
        
        # Determine difficulty based on user age if authenticated
        user = request.user if request.user.is_authenticated else None
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)
            age_difficulty = get_difficulty_by_age(user_age)
            if age_difficulty:
                # Use age-appropriate difficulty, but allow easier levels
                difficulty = age_difficulty
        
        # Get words for this type and difficulty, filtered by age
        base_query = CaptureWord.objects.filter(part_of_speech=pos)
        words_query = filter_by_age_appropriate(user, base_query, 'difficulty')
        words = list(words_query.filter(difficulty=difficulty))
        
        # If not enough words, get from easier difficulties (age-appropriate)
        if len(words) < count:
            if difficulty == 'hard':
                words += list(words_query.filter(difficulty='medium'))
            if difficulty in ['hard', 'medium']:
                words += list(words_query.filter(difficulty='easy'))
        
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
    """Get a mix of different parts of speech for Word Capture, filtered by user age"""
    difficulty = request.GET.get('difficulty', 'easy')
    target_type = request.GET.get('target', 'noun')
    target_count = int(request.GET.get('target_count', 5))
    other_count = int(request.GET.get('other_count', 3))
    
    try:
        # Get target words
        target_pos = CapturePartOfSpeech.objects.filter(name=target_type).first()
        if not target_pos:
            return JsonResponse({'error': 'Target type not found'}, status=404)
        
        # Determine difficulty based on user age if authenticated
        user = request.user if request.user.is_authenticated else None
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)
            age_difficulty = get_difficulty_by_age(user_age)
            if age_difficulty:
                difficulty = age_difficulty
        
        # Get target words, filtered by age
        base_query = CaptureWord.objects.filter(part_of_speech=target_pos)
        words_query = filter_by_age_appropriate(user, base_query, 'difficulty')
        target_words = list(words_query.filter(difficulty=difficulty))
        
        # Fallback to easier difficulties if needed (age-appropriate)
        if len(target_words) < target_count:
            if difficulty == 'hard':
                target_words += list(words_query.filter(difficulty='medium'))
            if difficulty in ['hard', 'medium']:
                target_words += list(words_query.filter(difficulty='easy'))
        
        if len(target_words) < target_count:
            return JsonResponse({'error': 'Not enough target words'}, status=404)
        
        selected_targets = random.sample(target_words, target_count)
        
        # Get other words (different parts of speech), filtered by age
        other_types = CapturePartOfSpeech.objects.exclude(name=target_type)
        other_words = []
        
        for pos in other_types:
            base_pos_query = CaptureWord.objects.filter(part_of_speech=pos)
            pos_words_query = filter_by_age_appropriate(user, base_pos_query, 'difficulty')
            words = list(pos_words_query.filter(difficulty=difficulty))
            
            # Fallback to easier difficulties (age-appropriate)
            if len(words) < 2:
                if difficulty == 'hard':
                    words += list(pos_words_query.filter(difficulty='medium'))
                if difficulty in ['hard', 'medium']:
                    words += list(pos_words_query.filter(difficulty='easy'))
            
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

def words_search(request):
    """Main word search game view"""
    return render(request, 'words_search.html')

def generate_word_search_puzzle(level_number, user=None):
    """Generate a word search puzzle for the given level, filtered by user age"""
    try:
        # Filter levels by age-appropriate difficulty
        levels = WordSearchLevel.objects.filter(level_number=level_number)
        levels_query = filter_by_age_appropriate(user, levels, 'difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
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
            # Generate puzzle on the fly (with age filtering)
            words = generate_words_for_level(level, category, user)
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

def generate_words_for_level(level, category, user=None):
    """Generate appropriate words for the level and category, filtered by user age"""
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
    """Get word search puzzle for a specific level, filtered by user age"""
    level_number = int(request.GET.get('level', 1))
    
    user = request.user if request.user.is_authenticated else None
    puzzle_data = generate_word_search_puzzle(level_number, user)
    
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
@never_cache
def profile_setup_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.profile_completed:
        return redirect('home')
    
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()   # no need to reassign profile
            messages.success(request, 'Profile setup completed successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please select an avatar.')
    else:
        form = ProfileSetupForm(instance=profile)
    
    return render(request, 'choose_avatar.html', {
        'form': form,
        'user': request.user,
    })

@require_http_methods(["GET", "POST"])
@never_cache
def logout_view(request):
    # Logout works for both regular Django auth and allauth
    # This handles both GET and POST requests
    
    # Clear all session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    messages.success(request, 'You have been logged out successfully.')
    
    # Create a response with no-cache headers to prevent back button access
    response = HttpResponseRedirect(reverse('login'))
    add_never_cache_headers(response)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@login_required
@never_cache
def home_view(request):
    if not request.user.profile.profile_completed:
        return redirect('profile_setup')
    response = render(request, 'homepage.html')
    add_never_cache_headers(response)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
@never_cache
def profile_view(request):
    user = request.user
    
    # Calculate total games played from all progress models
    games_played = 0
    total_points = 0
    highest_level = 1
    
    # Memory Match Game
    game_progress = UserGameProgress.objects.filter(user=user).first()
    if game_progress:
        games_played += game_progress.games_completed
        highest_level = max(highest_level, game_progress.highest_level)
    
    # Math Game
    math_progress = UserMathProgress.objects.filter(user=user).first()
    if math_progress:
        games_played += math_progress.games_played
        total_points += math_progress.total_score
        highest_level = max(highest_level, math_progress.highest_level)
    
    # Sentence Builder Game
    sentence_progress = UserSentenceProgress.objects.filter(user=user).first()
    if sentence_progress:
        games_played += sentence_progress.games_played
        total_points += sentence_progress.total_score
        highest_level = max(highest_level, sentence_progress.highest_level)
    
    # Word Search Game
    word_search_progress = UserWordSearchProgress.objects.filter(user=user).first()
    if word_search_progress:
        games_played += word_search_progress.games_played
        total_points += word_search_progress.total_score
        highest_level = max(highest_level, word_search_progress.highest_level)
    
    # Color Splash Game
    color_progress = UserColorProgress.objects.filter(user=user).first()
    if color_progress:
        games_played += color_progress.games_played
        total_points += color_progress.total_score
        highest_level = max(highest_level, color_progress.highest_level)
    
    # Quiz Game
    quizzes_taken = 0
    quiz_progress = UserQuizProgress.objects.filter(user=user).first()
    if quiz_progress:
        quizzes_taken = quiz_progress.games_played
        games_played += quiz_progress.games_played
        total_points += quiz_progress.total_score
        highest_level = max(highest_level, quiz_progress.highest_level)
    
    # Capture Words Game (from GameScore model)
    capture_scores = GameScore.objects.filter(user=user, game_name__icontains='capture')
    games_played += capture_scores.count()
    total_points += sum(score.score for score in capture_scores)
    
    user_stats = {
        'level': highest_level,
        'points': total_points,
        'games_played': games_played,
        'quizzes_taken': quizzes_taken
    }
    
    # Initialize recent activities list (can be enhanced later with actual activity data)
    recent_activities = []
    
    # Initialize forms
    change_password_form = ChangePasswordForm(user=user)
    edit_profile_form = EditProfileForm(user=user, instance=user.profile)
    
    # Handle form submissions via AJAX
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password_form = ChangePasswordForm(user=user, data=request.POST)
            if change_password_form.is_valid():
                change_password_form.save()
                messages.success(request, 'Your password has been changed successfully!')
                return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
            else:
                return JsonResponse({
                    'success': False,
                    'errors': change_password_form.errors
                }, status=400)
        
        elif 'edit_profile' in request.POST:
            edit_profile_form = EditProfileForm(user=user, instance=user.profile, data=request.POST)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
            else:
                return JsonResponse({
                    'success': False,
                    'errors': edit_profile_form.errors
                }, status=400)
    
    # Render the profile template
    response = render(request, 'profile.html', {
        'user_stats': user_stats,
        'recent_activities': recent_activities,
        'change_password_form': change_password_form,
        'edit_profile_form': edit_profile_form
    })
    
    # Add no-cache headers
    add_never_cache_headers(response)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response
    