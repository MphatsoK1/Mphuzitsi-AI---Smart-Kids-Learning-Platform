import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import QuizCategory, QuizQuestion, QuizLevel, QuizGameSession, UserQuizProgress
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age
from django.shortcuts import render

def quizes(request):
    return render(request, 'quizes/quizes.html')

def get_quiz_level(request):
    """Get quiz questions for a specific level, filtered by user age"""
    level_number = int(request.GET.get('level', 1))
    
    # Get list of already answered question IDs to exclude
    answered_ids_param = request.GET.get('answered_ids', '')
    answered_ids = []
    if answered_ids_param:
        try:
            answered_ids = [int(id) for id in answered_ids_param.split(',') if id.strip()]
        except ValueError:
            answered_ids = []
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = QuizLevel.objects.filter(level_number=level_number)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = QuizLevel.objects.get(level_number=level_number)
        
        # Filter categories by age-appropriate difficulty
        categories = QuizCategory.objects.filter(is_active=True)
        categories_query = filter_by_age_appropriate(user, categories, 'difficulty')
        
        # Use age-appropriate category if available
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)
            age_difficulty = get_difficulty_by_age(user_age)
            if age_difficulty:
                categories_query = categories_query.filter(difficulty=age_difficulty)
        
        # If no age-appropriate category, fall back to level's category
        if not categories_query.exists():
            categories_query = QuizCategory.objects.filter(pk=level.category.pk)
        
        # Filter questions by age-appropriate category, excluding already answered questions
        # This ensures questions from previous levels don't appear in new levels
        questions_query = QuizQuestion.objects.filter(
            category__in=categories_query.values_list('pk', flat=True),
            is_active=True
        )
        
        # Exclude already answered questions (from all previous levels)
        # This prevents any question from appearing again in subsequent levels
        if answered_ids:
            questions_query = questions_query.exclude(id__in=answered_ids)
        
        # Get required number of questions, or all available if not enough
        available_count = questions_query.count()
        questions_needed = level.questions_required
        
        if available_count < questions_needed:
            # If we don't have enough new questions for this difficulty level,
            # we need to either:
            # 1. Use all available questions (including previously answered ones)
            # 2. Or inform the user that more questions need to be added
            # For now, we'll use all available questions to prevent errors
            # But ideally, you should run: python manage.py seed_quizgame
            # to add more questions for each difficulty level
            remaining_questions = QuizQuestion.objects.filter(
                category__in=categories_query.values_list('pk', flat=True),
                is_active=True
            ).exclude(id__in=answered_ids if answered_ids else [])
            
            if remaining_questions.count() > 0:
                questions = remaining_questions.order_by('?')[:min(questions_needed, remaining_questions.count())]
            else:
                # All questions have been shown, reset for this difficulty
                questions = QuizQuestion.objects.filter(
                    category__in=categories_query.values_list('pk', flat=True),
                    is_active=True
                ).order_by('?')[:questions_needed]
        else:
            # Get random questions excluding already answered ones
            questions = questions_query.order_by('?')[:questions_needed]
        
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': question.id,
                'question_text': question.question_text,
                'options': question.get_options(),
                'correct_option': question.correct_option,
                'explanation': question.explanation,
                'points': question.points
            })
        
        level_data = {
            'level_number': level.level_number,
            'category': level.category.name,
            'difficulty': level.category.difficulty,
            'color': level.category.color,
            'icon': level.category.icon,
            'time_limit': level.time_limit,
            'questions_required': level.questions_required,
            'questions': questions_data
        }
        
        return JsonResponse(level_data)
        
    except QuizLevel.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def start_quiz_session(request):
    """Start a new quiz game session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        player_name = data.get('player_name', 'Player')
        
        user = request.user if request.user.is_authenticated else None
        
        session = QuizGameSession.objects.create(
            session_id=session_id,
            player_name=player_name,
            user=user,
            current_level=1,
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.session_id,
            'message': 'Quiz game session started'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_quiz_progress(request):
    """Update quiz game progress"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level')
        score = data.get('score')
        questions_answered = data.get('questions_answered')
        correct_answers = data.get('correct_answers')
        perfect_streak = data.get('perfect_streak', 0)
        time_spent = data.get('time_spent')
        
        session = QuizGameSession.objects.get(session_id=session_id)
        session.current_level = level
        session.total_score = score
        session.questions_answered = questions_answered
        session.correct_answers = correct_answers
        session.perfect_streak = perfect_streak
        session.time_spent = time_spent
        session.save()
        
        # Update user progress if authenticated
        if session.user:
            progress, created = UserQuizProgress.objects.get_or_create(
                user=session.user
            )
            if level > progress.highest_level:
                progress.highest_level = level
            progress.total_score += score
            progress.total_questions += questions_answered
            progress.correct_answers += correct_answers
            if correct_answers == questions_answered:  # Perfect quiz
                progress.perfect_quizzes += 1
            progress.games_played += 1
            progress.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_next_quiz_level(request):
    """Get next quiz level information, filtered by user age"""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = QuizLevel.objects.filter(level_number=next_level)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = QuizLevel.objects.get(level_number=next_level)
        
        return JsonResponse({
            'level_number': level.level_number,
            'category': level.category.name,
            'difficulty': level.category.difficulty,
            'unlock_score': level.unlock_score
        })
    except QuizLevel.DoesNotExist:
        return JsonResponse({'error': 'No more levels'}, status=404)

def get_quiz_categories(request):
    """Get all available quiz categories, filtered by user age"""
    categories = QuizCategory.objects.filter(is_active=True)
    user = request.user if request.user.is_authenticated else None
    categories_query = filter_by_age_appropriate(user, categories, 'difficulty')
    
    categories_data = [
        {
            'id': cat.id,
            'name': cat.name,
            'difficulty': cat.difficulty,
            'color': cat.color,
            'icon': cat.icon,
            'description': cat.description,
            'question_count': cat.questions.filter(is_active=True).count()
        }
        for cat in categories_query
    ]
    return JsonResponse({'categories': categories_data})