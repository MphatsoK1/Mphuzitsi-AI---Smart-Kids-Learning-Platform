import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import QuizCategory, QuizQuestion, QuizLevel, QuizGameSession, UserQuizProgress
from django.shortcuts import render

def quizes(request):
    return render(request, 'quizes/quizes.html')

def get_quiz_level(request):
    """Get quiz questions for a specific level"""
    level_number = int(request.GET.get('level', 1))
    
    try:
        level = QuizLevel.objects.get(level_number=level_number)
        questions = QuizQuestion.objects.filter(
            category=level.category,
            is_active=True
        ).order_by('?')[:level.questions_required]  # Random selection
        
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
    """Get next quiz level information"""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1
    
    try:
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
    """Get all available quiz categories"""
    categories = QuizCategory.objects.filter(is_active=True)
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
        for cat in categories
    ]
    return JsonResponse({'categories': categories_data})