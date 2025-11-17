import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import MathGameLevel, MathGameProblem, MathGameSession, UserMathProgress
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age
from django.shortcuts import render

def math_game(request):
    return render(request, 'math_game/math_game.html')

def generate_math_problem(level, user=None):
    """Generate a math problem based on level configuration, adjusted for user age"""
    level_config = MathGameLevel.objects.get(level_number=level)
    operations = level_config.operations
    min_num = level_config.number_range_min
    max_num = level_config.number_range_max
    
    # Adjust difficulty based on user age
    if user and hasattr(user, 'profile') and user.profile.date_of_birth:
        user_age = get_age_from_birthdate(user.profile.date_of_birth)
        if user_age:
            # Adjust number ranges based on age
            if user_age <= 6:
                # Ages 3-6: easier numbers
                max_num = min(max_num, 10)
            elif user_age <= 9:
                # Ages 7-9: medium numbers
                max_num = min(max_num, 20)
            # Ages 10+: keep original ranges
    
    operation = random.choice(operations)
    
    if operation == '+':
        num1 = random.randint(min_num, max_num)
        num2 = random.randint(min_num, max_num)
        answer = num1 + num2
        problem_text = f"{num1} + {num2}"
        display_text = f"{num1} + {num2} = ?"
        
    elif operation == '-':
        num1 = random.randint(min_num, max_num)
        num2 = random.randint(min_num, num1)  # Ensure positive result
        answer = num1 - num2
        problem_text = f"{num1} - {num2}"
        display_text = f"{num1} - {num2} = ?"
        
    elif operation == '×':
        num1 = random.randint(min_num, max_num)
        num2 = random.randint(min_num, min(5, max_num))  # Keep multiplication manageable
        answer = num1 * num2
        problem_text = f"{num1} × {num2}"
        display_text = f"{num1} × {num2} = ?"
        
    elif operation == '÷':
        # Ensure division results in integer
        num2 = random.randint(1, max_num)
        answer = random.randint(min_num, max_num)
        num1 = num2 * answer
        problem_text = f"{num1} ÷ {num2}"
        display_text = f"{num1} ÷ {num2} = ?"
    
    return {
        'problem_text': problem_text,
        'display_text': display_text,
        'correct_answer': answer,
        'operation': operation
    }

def get_math_level(request):
    """Get math problems for a specific level, filtered by user age"""
    level_number = int(request.GET.get('level', 1))
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = MathGameLevel.objects.filter(level_number=level_number)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = MathGameLevel.objects.get(level_number=level_number)
        
        # Generate problems on the fly (age-adjusted)
        problems = []
        for _ in range(level.problems_required):
            problem = generate_math_problem(level_number, user)
            problems.append(problem)
        
        level_data = {
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'time_limit': level.time_limit,
            'problems_required': level.problems_required,
            'points_per_problem': level.points_per_problem,
            'operations': level.operations,
            'problems': problems
        }
        
        return JsonResponse(level_data)
        
    except MathGameLevel.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def start_math_session(request):
    """Start a new math game session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        player_name = data.get('player_name', 'Player')
        
        user = request.user if request.user.is_authenticated else None
        
        session = MathGameSession.objects.create(
            session_id=session_id,
            player_name=player_name,
            user=user,
            current_level=1,
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.session_id,
            'message': 'Math game session started'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_math_progress(request):
    """Update math game progress"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level')
        score = data.get('score')
        problems_completed = data.get('problems_completed')
        perfect_streak = data.get('perfect_streak', 0)
        total_attempts = data.get('total_attempts')
        correct_attempts = data.get('correct_attempts')
        time_spent = data.get('time_spent')
        
        session = MathGameSession.objects.get(session_id=session_id)
        session.current_level = level
        session.total_score = score
        session.problems_completed = problems_completed
        session.perfect_streak = perfect_streak
        session.total_attempts = total_attempts
        session.correct_attempts = correct_attempts
        session.time_spent = time_spent
        session.save()
        
        # Update user progress if authenticated
        if session.user:
            progress, created = UserMathProgress.objects.get_or_create(
                user=session.user
            )
            if level > progress.highest_level:
                progress.highest_level = level
            progress.total_score += score
            progress.total_problems += problems_completed
            progress.perfect_streaks = max(progress.perfect_streaks, perfect_streak)
            progress.games_played += 1
            progress.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_next_math_level(request):
    """Get next math level information, filtered by user age"""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = MathGameLevel.objects.filter(level_number=next_level)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = MathGameLevel.objects.get(level_number=next_level)
        
        return JsonResponse({
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'unlock_score': level.unlock_score
        })
    except MathGameLevel.DoesNotExist:
        return JsonResponse({'error': 'No more levels'}, status=404)