import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import QuizCategory, QuizQuestion, QuizLevel, QuizGameSession, UserQuizProgress
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age
from django.shortcuts import render
from .ai_question_generator import generate_ai_question, create_unique_fallback_question

def quizes(request):
    return render(request, 'quizes/quizes.html')    

def get_quiz_level(request):
    """Get quiz questions for a specific level, mixing AI and database questions"""
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
        
        # Get available database questions (excluding answered ones)
        questions_query = QuizQuestion.objects.filter(
            category__in=categories_query.values_list('pk', flat=True),
            is_active=True
        )
        
        # Exclude already answered questions
        if answered_ids:
            questions_query = questions_query.exclude(id__in=answered_ids)
        
        # Get available database questions
        available_db_questions = list(questions_query.order_by('?'))  # Random order
        available_count = len(available_db_questions)
        questions_needed = level.questions_required
        
        questions_data = []
        
        # Define points based on difficulty
        difficulty_points_map = {
            'easy': 10,
            'medium': 15,
            'hard': 20,
            'expert': 25
        }
        
        current_difficulty = level.category.difficulty
        points = difficulty_points_map.get(current_difficulty, 10)
        
        # Get category for AI questions context
        category = categories_query.first()
        topic = category.name if category else "general knowledge"
        
        # Get user age for AI question generation
        user_age = 10  # default
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)


        # STRATEGY: Use AI questions first, fallback to database questions when AI fails
        ai_questions_count = 0
        db_questions_count = 0

        for i in range(questions_needed):
            # Try AI question first
            try:
                ai_question = generate_ai_question(
                    difficulty=current_difficulty,
                    age=user_age,
                    topic=topic,
                    question_number=i + 1
                )
                
                questions_data.append({
                    'id': f"ai_{level_number}_{i}_{random.randint(1000,9999)}",
                    'question_text': ai_question['question'],
                    'options': [
                        {'letter': 'A', 'text': ai_question['options'][0]},
                        {'letter': 'B', 'text': ai_question['options'][1]},
                        {'letter': 'C', 'text': ai_question['options'][2]},
                        {'letter': 'D', 'text': ai_question['options'][3]}
                    ],
                    'correct_option': ai_question['correct'],
                    'explanation': ai_question['explanation'],
                    'points': points,
                    'is_ai': True
                })
                ai_questions_count += 1
                
            except Exception as e:
                print(f"Error generating AI question: {e}")
                # AI failed, use database question as fallback
                if available_db_questions:
                    db_question = available_db_questions.pop(0)
                    questions_data.append({
                        'id': db_question.id,
                        'question_text': db_question.question_text,
                        'options': db_question.get_options(),
                        'correct_option': db_question.correct_option,
                        'explanation': db_question.explanation,
                        'points': db_question.points,
                        'is_ai': False
                    })
                    db_questions_count += 1
                else:
                    # Last resort: use simple fallback
                    questions_data.append(create_unique_fallback_question(level_number, i, current_difficulty, topic))
        
        # Shuffle the final questions to mix AI and database questions randomly
        #random.shuffle(questions_data)
        
        level_data = {
            'level_number': level.level_number,
            'category': level.category.name,
            'difficulty': current_difficulty,
            'color': level.category.color,
            'icon': level.category.icon,
            'time_limit': level.time_limit,
            'questions_required': level.questions_required,
            'questions': questions_data,
            'ai_questions_count': ai_questions_count,
            'db_questions_count': db_questions_count
        }
        
        print(f"Level {level_number}: {db_questions_count} DB questions, {ai_questions_count} AI questions")
        
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


@csrf_exempt
def get_next_question(request):
    user = request.user
    
    # Example simple difficulty rule:
    difficulty = "easy"  # or "medium" / "hard"
    
    question_data = generate_ai_question(
        difficulty=difficulty,
        age=user.profile.age if hasattr(user, "profile") else 10,
        topic="mathematics"  # can change dynamically
    )

    return JsonResponse(question_data, safe=False)
