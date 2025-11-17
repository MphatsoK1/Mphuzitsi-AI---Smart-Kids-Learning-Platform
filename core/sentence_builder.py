import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SentenceBuilderLevel, SentenceBuilderSentence, SentenceBuilderGameSession, UserSentenceProgress
from .game_utils import filter_by_age_appropriate, get_age_from_birthdate, get_difficulty_by_age
from django.shortcuts import render

def sentence_builder(request):
    return render(request, 'sentence_builder/sentence_builder.html')

def get_level_sentences(request):
    """Get sentences for a specific level, filtered by user age"""
    level_number = int(request.GET.get('level', 1))
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = SentenceBuilderLevel.objects.filter(level_number=level_number)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = SentenceBuilderLevel.objects.get(level_number=level_number)
        
        # Filter sentences by age-appropriate level
        sentences = SentenceBuilderSentence.objects.filter(
            level=level,
            is_active=True
        ).order_by('?')[:level.sentences_required]  # Random selection
        
        sentences_data = []
        for sentence_obj in sentences:
            sentences_data.append({
                'id': sentence_obj.id,
                'correct': sentence_obj.sentence,
                'scrambled': sentence_obj.get_scrambled_words(),
                'hint': sentence_obj.hint,
                'word_count': sentence_obj.word_count
            })
        
        level_data = {
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'time_limit': level.time_limit,
            'sentences_required': level.sentences_required,
            'points_per_sentence': level.points_per_sentence,
            'sentences': sentences_data
        }
        
        return JsonResponse(level_data)
        
    except SentenceBuilderLevel.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def start_sentence_session(request):
    """Start a new game session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        player_name = data.get('player_name', 'Player')
        
        # Get or create user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        session = SentenceBuilderGameSession.objects.create(
            session_id=session_id,
            player_name=player_name,
            user=user,
            current_level=1,
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.session_id,
            'message': 'Game session started'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_sentence_progress(request):
    """Update game progress"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level')
        score = data.get('score')
        sentences_completed = data.get('sentences_completed')
        perfect_sentences = data.get('perfect_sentences', 0)
        total_attempts = data.get('total_attempts')
        correct_attempts = data.get('correct_attempts')
        time_spent = data.get('time_spent')
        
        session = SentenceBuilderGameSession.objects.get(session_id=session_id)
        session.current_level = level
        session.total_score = score
        session.sentences_completed = sentences_completed
        session.perfect_sentences = perfect_sentences
        session.total_attempts = total_attempts
        session.correct_attempts = correct_attempts
        session.time_spent = time_spent
        session.save()
        
        # Update user progress if authenticated
        if session.user:
            progress, created = UserSentenceProgress.objects.get_or_create(
                user=session.user
            )
            if level > progress.highest_level:
                progress.highest_level = level
            progress.total_score += score
            progress.total_sentences += sentences_completed
            progress.perfect_sentences += perfect_sentences
            progress.games_played += 1
            progress.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_next_level(request):
    """Get next level information, filtered by user age"""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = SentenceBuilderLevel.objects.filter(level_number=next_level)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = SentenceBuilderLevel.objects.get(level_number=next_level)
        
        return JsonResponse({
            'level_number': level.level_number,
            'difficulty': level.difficulty,
            'unlock_score': level.unlock_score
        })
    except SentenceBuilderLevel.DoesNotExist:
        return JsonResponse({'error': 'No more levels'}, status=404)