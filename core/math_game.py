import json
import random
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import MathGameLevel, MathGameProblem, MathGameSession, UserMathProgress
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age
from .ai_math_generator import generate_ai_math_problem

logger = logging.getLogger(__name__)

def math_game(request):
    return render(request, 'math_game/math_game.html')

def build_math_tip(operation):
    tips = {
        '+': "Addition combines numbers to make a larger number.",
        '-': "Subtraction finds the difference between two numbers.",
        '×': "Multiplication is repeated addition.",
        '÷': "Division splits a number into equal groups."
    }
    return tips.get(operation, "Break the problem into smaller steps.")

def build_math_hint(operation, num1, num2):
    if operation == '+':
        return f"Start by adding {num1} and {num2} tens and then the ones."
    if operation == '-':
        return f"Think of how much you subtract from {num1} to reach {num2}."
    if operation == '×':
        return f"Try adding {num1} together {num2} times."
    if operation == '÷':
        return f"See how many groups of {num2} fit into {num1}."
    return "Look at the numbers carefully and solve step by step."

def generate_math_problem(level, user=None, level_config=None):
    """Generate a math problem based on level configuration, adjusted for user age"""
    level_config = level_config or MathGameLevel.objects.get(level_number=level)
    operations = level_config.operations or ['+']
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
        'operation': operation,
        'tip': build_math_tip(operation),
        'hint': build_math_hint(operation, num1, num2),
        'explanation': f"{problem_text} = {answer}",
        'is_ai': False
    }

def serialize_db_problem(db_problem):
    problem_text = db_problem.problem_text
    display_text = f"{problem_text} = ?" if '=' not in problem_text else problem_text
    num1, num2 = extract_numbers(problem_text)
    return {
        'problem_text': problem_text,
        'display_text': display_text,
        'correct_answer': db_problem.correct_answer,
        'operation': db_problem.operation,
        'tip': build_math_tip(db_problem.operation),
        'hint': db_problem.hint or build_math_hint(db_problem.operation, num1, num2),
        'explanation': f"{problem_text} = {db_problem.correct_answer}",
        'is_ai': False
    }

def extract_numbers(problem_text):
    try:
        cleaned = problem_text.replace('×', '*').replace('÷', '/')
        parts = cleaned.replace('=', '').split()
        numbers = [int(part) for part in parts if part.strip().isdigit()]
        if len(numbers) >= 2:
            return numbers[0], numbers[1]
    except Exception:
        pass
    return 0, 0

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
        
        user_age = None
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)
        
        db_problems = list(MathGameProblem.objects.filter(level=level, is_active=True))
        random.shuffle(db_problems)
        
        problems = []
        ai_problems_count = 0
        db_problems_count = 0
        
        for idx in range(level.problems_required):
            problem = None
            try:
                problem = generate_ai_math_problem(
                    difficulty=level.difficulty,
                    operations=level.operations,
                    min_value=level.number_range_min,
                    max_value=level.number_range_max,
                    age=user_age or 10,
                    problem_number=idx + 1
                )
                problem['display_text'] = problem.get('display_text') or f"{problem.get('problem_text')} = ?"
                problem['tip'] = problem.get('tip') or build_math_tip(problem.get('operation', '+'))
                problem['hint'] = problem.get('hint') or build_math_hint(problem.get('operation', '+'), 0, 0)
                problem['explanation'] = problem.get('explanation') or f"{problem['problem_text']} = {problem['correct_answer']}"
                problem['is_ai'] = True
                ai_problems_count += 1
            except Exception as exc:
                logger.debug("AI math problem failed: %s", exc)
                if db_problems:
                    db_problem = db_problems.pop(0)
                    problem = serialize_db_problem(db_problem)
                    db_problems_count += 1
                else:
                    problem = generate_math_problem(level_number, user, level_config=level)
            problems.append(problem)
        
        level_data = {
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'time_limit': level.time_limit,
            'problems_required': level.problems_required,
            'points_per_problem': level.points_per_problem,
            'operations': level.operations,
            'problems': problems,
            'ai_problems_count': ai_problems_count,
            'db_problems_count': db_problems_count
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