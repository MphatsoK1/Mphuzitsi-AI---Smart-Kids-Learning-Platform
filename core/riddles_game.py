# import json
# import random
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# from django.shortcuts import render
# from django.db import transaction
# from .models import (
#     RiddleCategory,
#     RiddleQuestion,
#     RiddleLevel,
#     RiddleGameSession,
#     UserRiddleProgress,
#     QuizLevel,
# )
# from .game_utils import (
#     filter_by_age_appropriate,
#     get_age_from_birthdate,
#     get_difficulty_by_age,
# )
# from .ai_riddles_generator import generate_ai_riddle, create_unique_fallback_riddle

# # Remove the hardcoded DISTRACTOR_FALLBACKS entirely

# def generate_options(correct_answer, answer_pool, distractors=None, num_options=4):
#     """Generate multiple-choice options using AI distractors when available."""
#     options = []
#     normalized = set()

#     def add_option(value):
#         if not value:
#             return
#         key = value.strip().lower()
#         if key and key not in normalized:
#             normalized.add(key)
#             options.append(value.strip())

#     # Always add the correct answer first
#     add_option(correct_answer)

#     # Priority 1: Use AI-generated distractors if provided
#     if distractors:
#         for distractor in distractors:
#             if len(options) >= num_options:
#                 break
#             add_option(distractor)
    
#     # Priority 2: Use answers from other questions in the pool
#     if len(options) < num_options:
#         distractors_from_pool = [
#             ans for ans in answer_pool 
#             if ans and ans.strip().lower() != correct_answer.strip().lower()
#         ]
#         random.shuffle(distractors_from_pool)
        
#         for ans in distractors_from_pool:
#             if len(options) >= num_options:
#                 break
#             add_option(ans)
    
#     # Priority 3: Simple fallback generation based on answer characteristics
#     if len(options) < num_options:
#         # Generate context-aware fallbacks based on the correct answer
#         context_fallbacks = generate_context_fallbacks(correct_answer, num_options - len(options))
#         for fallback in context_fallbacks:
#             if len(options) >= num_options:
#                 break
#             add_option(fallback)

#     # Final shuffle to randomize position
#     random.shuffle(options)
#     return options

# def generate_context_fallbacks(correct_answer, num_needed):
#     """Generate context-aware fallback options based on the correct answer."""
#     if not correct_answer:
#         return []
    
#     answer_lower = correct_answer.lower().strip()
#     fallbacks = []
    
#     # Common patterns for riddle answers
#     common_patterns = [
#         # For object-based answers
#         ["A rock", "A tree", "A cloud", "The sun", "The moon"],
#         # For concept-based answers
#         ["Time", "Wind", "Light", "Darkness", "Silence"],
#         # For animal-based answers
#         ["A cat", "A dog", "A bird", "A fish", "A horse"],
#         # For household items
#         ["A chair", "A table", "A door", "A window", "A mirror"],
#     ]
    
#     # Try to match pattern based on answer content
#     selected_pattern = random.choice(common_patterns)
    
#     # Filter out the correct answer and take needed number
#     filtered_fallbacks = [fb for fb in selected_pattern if fb.lower() != answer_lower]
#     return filtered_fallbacks[:num_needed]

# def build_tip(question_text, answer):
#     """Create a friendly tip that nudges the player toward the answer."""
#     length_hint = f"The answer has {len(answer)} letters."
#     if '?' in question_text:
#         question_text = question_text.replace('?', '')
#     if len(answer.split()) > 1:
#         length_hint = f"The answer has {len(answer.split())} words."
#     patterns = [
#         "Think about everyday objects that match this description.",
#         "Pay attention to the wordplay in the riddle.",
#         "Sometimes the most obvious answer is the right one.",
#         "Imagine you are looking around the room—what fits?",
#         "Try to visualize what the riddle is describing.",
#         length_hint
#     ]
#     random.shuffle(patterns)
#     return patterns[0]

# def build_hint(answer):
#     """Derive a hint string from the answer."""
#     if not answer:
#         return "Look closely at the riddle details."
#     if len(answer) <= 4:
#         return f"The answer starts with '{answer[0].upper()}'."
#     return f"The answer starts with '{answer[0].upper()}' and ends with '{answer[-1].upper()}'."

# LEVELS_SYNCED = False

# def sync_riddle_levels_from_quiz():
#     """Ensure riddles share the same level structure as the quiz game."""
#     global LEVELS_SYNCED
#     if LEVELS_SYNCED:
#         return

#     with transaction.atomic():
#         quiz_levels = QuizLevel.objects.select_related('category').all()

#         for quiz_level in quiz_levels:
#             quiz_cat = quiz_level.category
#             riddle_category, created = RiddleCategory.objects.get_or_create(
#                 name=quiz_cat.name,
#                 defaults={
#                     'difficulty': quiz_cat.difficulty,
#                     'description': quiz_cat.description,
#                     'color': quiz_cat.color,
#                     'icon': quiz_cat.icon,
#                     'is_active': quiz_cat.is_active,
#                 }
#             )

#             if not created:
#                 updated = False
#                 for field in ['difficulty', 'description', 'color', 'icon', 'is_active']:
#                     quiz_value = getattr(quiz_cat, field)
#                     if getattr(riddle_category, field) != quiz_value:
#                         setattr(riddle_category, field, quiz_value)
#                         updated = True
#                 if updated:
#                     riddle_category.save()

#             riddle_level, created = RiddleLevel.objects.get_or_create(
#                 level_number=quiz_level.level_number,
#                 defaults={
#                     'category': riddle_category,
#                     'questions_required': quiz_level.questions_required,
#                     'time_limit': quiz_level.time_limit,
#                     'unlock_score': quiz_level.unlock_score,
#                 }
#             )

#             if not created:
#                 needs_save = False
#                 if riddle_level.category != riddle_category:
#                     riddle_level.category = riddle_category
#                     needs_save = True
#                 for field in ['questions_required', 'time_limit', 'unlock_score']:
#                     quiz_val = getattr(quiz_level, field)
#                     if getattr(riddle_level, field) != quiz_val:
#                         setattr(riddle_level, field, quiz_val)
#                         needs_save = True
#                 if needs_save:
#                     riddle_level.save()

#     LEVELS_SYNCED = True

# def riddles_game(request):
#     """Main riddles game view."""
#     return render(request, 'riddles/riddles.html')

# # Backwards compatibility for any legacy imports
# riddles = riddles_game    

# def get_riddle_level(request):
#     """Get riddle questions for a specific level, mixing AI and database questions"""
#     level_number = int(request.GET.get('level', 1))
    
#     sync_riddle_levels_from_quiz()
    
#     # Get list of already answered question IDs to exclude
#     answered_ids_param = request.GET.get('answered_ids', '')
#     answered_ids = []
#     if answered_ids_param:
#         for raw_id in answered_ids_param.split(','):
#             raw_id = raw_id.strip()
#             if raw_id.isdigit():
#                 answered_ids.append(int(raw_id))
    
#     try:
#         # Filter levels by age-appropriate difficulty
#         levels = RiddleLevel.objects.filter(level_number=level_number)
#         user = request.user if request.user.is_authenticated else None
#         levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
#         level = levels_query.first()
        
#         if not level:
#             # Fallback to default level if age filtering removes it
#             level = RiddleLevel.objects.get(level_number=level_number)
        
#         # Filter categories by age-appropriate difficulty
#         categories = RiddleCategory.objects.filter(is_active=True)
#         categories_query = filter_by_age_appropriate(user, categories, 'difficulty')
        
#         # Use age-appropriate category if available
#         if user and hasattr(user, 'profile') and user.profile.date_of_birth:
#             user_age = get_age_from_birthdate(user.profile.date_of_birth)
#             age_difficulty = get_difficulty_by_age(user_age)
#             if age_difficulty:
#                 categories_query = categories_query.filter(difficulty=age_difficulty)
        
#         # If no age-appropriate category, fall back to level's category
#         if not categories_query.exists():
#             categories_query = RiddleCategory.objects.filter(pk=level.category.pk)
        
#         # Get available database questions (excluding answered ones)
#         questions_query = RiddleQuestion.objects.filter(
#             category__in=categories_query.values_list('pk', flat=True),
#             is_active=True
#         )
#         answer_pool = list(
#             RiddleQuestion.objects.filter(is_active=True).values_list('answer', flat=True)
#         )
        
#         # Exclude already answered questions
#         if answered_ids:
#             questions_query = questions_query.exclude(id__in=answered_ids)
        
#         # Get available database questions
#         available_db_questions = list(questions_query.order_by('?'))  # Random order
#         riddles_needed = level.questions_required
#         questions_data = []
        
#         current_difficulty = level.category.difficulty
        
#         # Get category for AI questions context
#         category = categories_query.first()
#         topic = category.name if category else "general knowledge"
        
#         # Get user age for AI question generation
#         user_age = 10  # default
#         if user and hasattr(user, 'profile') and user.profile.date_of_birth:
#             user_age = get_age_from_birthdate(user.profile.date_of_birth)

#         # STRATEGY: Use AI riddles first, fallback to database riddles when AI fails
#         ai_riddles_count = 0
#         db_riddles_count = 0

#         for i in range(riddles_needed):
#             # Try AI riddle first
#             try:
#                 ai_riddle = generate_ai_riddle(
#                     difficulty=current_difficulty,
#                     age=user_age,
#                     topic=topic,
#                     riddle_number=i + 1
#                 )
                
#                 # Use AI-generated distractors when available
#                 ai_distractors = ai_riddle.get('distractors', [])
                
#                 questions_data.append({
#                     'id': f"ai_{level_number}_{i}_{random.randint(1000,9999)}",
#                     'question_text': ai_riddle['question'],
#                     'answer': ai_riddle['answer'],
#                     'explanation': ai_riddle['explanation'],
#                     'is_ai': True,
#                     'options': generate_options(ai_riddle['answer'], answer_pool, ai_distractors),
#                     'tip': build_tip(ai_riddle['question'], ai_riddle['answer']),
#                     'hint': ai_riddle.get('hint') or build_hint(ai_riddle['answer'])
#                 })
#                 ai_riddles_count += 1
                
#             except Exception as e:
#                 print(f"Error generating AI riddle: {e}")
#                 # AI failed, use database question as fallback
#                 if available_db_questions:
#                     db_question = available_db_questions.pop(0)
#                     questions_data.append({
#                         'id': db_question.id,
#                         'question_text': db_question.question_text,
#                         'answer': db_question.answer,
#                         'explanation': db_question.explanation,
#                         'is_ai': False,
#                         'options': generate_options(db_question.answer, answer_pool),
#                         'tip': build_tip(db_question.question_text, db_question.answer),
#                         'hint': build_hint(db_question.answer)
#                     })
#                     db_riddles_count += 1
#                 else:
#                     # Last resort: use simple fallback
#                     fallback_riddle = create_unique_fallback_riddle(level_number, i, current_difficulty, topic)
#                     questions_data.append({
#                         'id': f"fallback_{level_number}_{i}",
#                         'question_text': fallback_riddle['question'],
#                         'answer': fallback_riddle['answer'],
#                         'explanation': fallback_riddle['explanation'],
#                         'is_ai': False,
#                         'options': generate_options(fallback_riddle['answer'], answer_pool),
#                         'tip': build_tip(fallback_riddle['question'], fallback_riddle['answer']),
#                         'hint': fallback_riddle.get('hint') or build_hint(fallback_riddle['answer'])
#                     })
        
#         # Shuffle the final riddles
#         random.shuffle(questions_data)
        
#         level_data = {
#             'level_number': level.level_number,
#             'category': level.category.name,
#             'difficulty': current_difficulty,
#             'color': level.category.color,
#             'icon': level.category.icon,
#             'time_limit': level.time_limit,
#             'riddles_required': level.questions_required,
#             'questions': questions_data,
#             'ai_riddles_count': ai_riddles_count,
#             'db_riddles_count': db_riddles_count
#         }
        
#         print(f"Level {level_number}: {db_riddles_count} DB riddles, {ai_riddles_count} AI riddles")
        
#         return JsonResponse(level_data)
        
#     except RiddleLevel.DoesNotExist:
#         return JsonResponse({'error': 'Level not found'}, status=404)

# @csrf_exempt
# @require_http_methods(["POST"])
# def start_riddle_session(request):
#     """Start a new riddle game session"""
#     try:
#         data = json.loads(request.body)
#         session_id = data.get('session_id')
#         player_name = data.get('player_name', 'Player')
        
#         user = request.user if request.user.is_authenticated else None
        
#         session = RiddleGameSession.objects.create(
#             session_id=session_id,
#             player_name=player_name,
#             user=user,
#             current_level=1,
#             is_active=True
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'session_id': session.session_id,
#             'message': 'Riddle game session started'
#         })
        
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# @csrf_exempt
# @require_http_methods(["POST"])
# def update_riddle_progress(request):
#     """Update riddle game progress for a session and user."""
#     try:
#         data = json.loads(request.body)
#         session_id = data.get('session_id')
#         level = data.get('level')
#         score = data.get('score')
#         questions_answered = data.get('questions_answered')
#         correct_answers = data.get('correct_answers')
#         perfect_streak = data.get('perfect_streak', 0)
#         time_spent = data.get('time_spent')

#         session = RiddleGameSession.objects.get(session_id=session_id)
#         session.current_level = level
#         session.total_score = score
#         session.questions_answered = questions_answered
#         session.correct_answers = correct_answers
#         session.perfect_streak = perfect_streak
#         session.time_spent = time_spent
#         session.save()

#         if session.user:
#             progress, _ = UserRiddleProgress.objects.get_or_create(user=session.user)
#             if level > progress.highest_level:
#                 progress.highest_level = level
#             progress.total_score += score
#             progress.total_questions += questions_answered
#             progress.correct_answers += correct_answers
#             if questions_answered and correct_answers == questions_answered:
#                 progress.perfect_riddles += 1
#             progress.games_played += 1
#             progress.save()

#         return JsonResponse({'status': 'success'})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# def get_next_riddle_level(request):
#     """Return metadata for the next riddle level."""
#     current_level = int(request.GET.get('current_level', 1))
#     next_level = current_level + 1

#     try:
#         levels = RiddleLevel.objects.filter(level_number=next_level)
#         user = request.user if request.user.is_authenticated else None
#         levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
#         level = levels_query.first()

#         if not level:
#             level = RiddleLevel.objects.get(level_number=next_level)

#         return JsonResponse({
#             'level_number': level.level_number,
#             'category': level.category.name,
#             'difficulty': level.category.difficulty,
#             'unlock_score': level.unlock_score
#         })
#     except RiddleLevel.DoesNotExist:
#         return JsonResponse({'error': 'No more levels'}, status=404)


# def get_riddle_categories(request):
#     """List active riddle categories filtered by age difficulty."""
#     categories = RiddleCategory.objects.filter(is_active=True)
#     user = request.user if request.user.is_authenticated else None
#     categories_query = filter_by_age_appropriate(user, categories, 'difficulty')

#     categories_data = [
#         {
#             'id': cat.id,
#             'name': cat.name,
#             'difficulty': cat.difficulty,
#             'color': cat.color,
#             'icon': cat.icon,
#             'description': cat.description,
#             'riddle_count': cat.questions.filter(is_active=True).count()
#         }
#         for cat in categories_query
#     ]
#     return JsonResponse({'categories': categories_data})


# @csrf_exempt
# def get_next_riddle(request):
#     """Return a single AI-generated riddle (quick play)."""
#     user = request.user
#     difficulty = "easy"

#     riddle_data = generate_ai_riddle(
#         difficulty=difficulty,
#         age=user.profile.age if hasattr(user, "profile") else 10,
#         topic="riddles"
#     )

#     return JsonResponse(riddle_data, safe=False)


import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.db import transaction, models
from django.core.cache import cache
from .models import (
    RiddleCategory,
    RiddleQuestion,
    RiddleLevel,
    RiddleGameSession,
    UserRiddleProgress,
    QuizLevel,
)
from .game_utils import (
    filter_by_age_appropriate,
    get_age_from_birthdate,
    get_difficulty_by_age,
)
from .ai_riddles_generator import generate_ai_riddle, create_unique_fallback_riddle

# Cache keys for tracking used riddles
def get_used_riddles_cache_key(session_id, level_number):
    return f"used_riddles_{session_id}_level_{level_number}"

def get_global_used_riddles_cache_key(user_id=None):
    if user_id:
        return f"global_used_riddles_user_{user_id}"
    return "global_used_riddles_anonymous"

def generate_options(correct_answer, answer_pool, distractors=None, num_options=4):
    """Generate multiple-choice options using AI distractors when available."""
    options = []
    normalized = set()

    def add_option(value):
        if not value:
            return
        key = value.strip().lower()
        if key and key not in normalized:
            normalized.add(key)
            options.append(value.strip())

    # Always add the correct answer first
    add_option(correct_answer)

    # Priority 1: Use AI-generated distractors if provided
    if distractors:
        for distractor in distractors:
            if len(options) >= num_options:
                break
            add_option(distractor)
    
    # Priority 2: Use answers from other questions in the pool
    if len(options) < num_options:
        distractors_from_pool = [
            ans for ans in answer_pool 
            if ans and ans.strip().lower() != correct_answer.strip().lower()
        ]
        random.shuffle(distractors_from_pool)
        
        for ans in distractors_from_pool:
            if len(options) >= num_options:
                break
            add_option(ans)
    
    # Priority 3: Simple fallback generation based on answer characteristics
    if len(options) < num_options:
        # Generate context-aware fallbacks based on the correct answer
        context_fallbacks = generate_context_fallbacks(correct_answer, num_options - len(options))
        for fallback in context_fallbacks:
            if len(options) >= num_options:
                break
            add_option(fallback)

    # Final shuffle to randomize position
    random.shuffle(options)
    return options

def generate_context_fallbacks(correct_answer, num_needed):
    """Generate context-aware fallback options based on the correct answer."""
    if not correct_answer:
        return []
    
    answer_lower = correct_answer.lower().strip()
    fallbacks = []
    
    # Common patterns for riddle answers
    common_patterns = [
        # For object-based answers
        ["A rock", "A tree", "A cloud", "The sun", "The moon"],
        # For concept-based answers
        ["Time", "Wind", "Light", "Darkness", "Silence"],
        # For animal-based answers
        ["A cat", "A dog", "A bird", "A fish", "A horse"],
        # For household items
        ["A chair", "A table", "A door", "A window", "A mirror"],
    ]
    
    # Try to match pattern based on answer content
    selected_pattern = random.choice(common_patterns)
    
    # Filter out the correct answer and take needed number
    filtered_fallbacks = [fb for fb in selected_pattern if fb.lower() != answer_lower]
    return filtered_fallbacks[:num_needed]

def build_tip(question_text, answer):
    """Create a friendly tip that nudges the player toward the answer."""
    length_hint = f"The answer has {len(answer)} letters."
    if '?' in question_text:
        question_text = question_text.replace('?', '')
    if len(answer.split()) > 1:
        length_hint = f"The answer has {len(answer.split())} words."
    patterns = [
        "Think about everyday objects that match this description.",
        "Pay attention to the wordplay in the riddle.",
        "Sometimes the most obvious answer is the right one.",
        "Imagine you are looking around the room—what fits?",
        "Try to visualize what the riddle is describing.",
        length_hint
    ]
    random.shuffle(patterns)
    return patterns[0]

def build_hint(answer):
    """Derive a hint string from the answer."""
    if not answer:
        return "Look closely at the riddle details."
    if len(answer) <= 4:
        return f"The answer starts with '{answer[0].upper()}'."
    return f"The answer starts with '{answer[0].upper()}' and ends with '{answer[-1].upper()}'."

LEVELS_SYNCED = False

def sync_riddle_levels_from_quiz():
    """Ensure riddles share the same level structure as the quiz game."""
    global LEVELS_SYNCED
    if LEVELS_SYNCED:
        return

    with transaction.atomic():
        quiz_levels = QuizLevel.objects.select_related('category').all()

        for quiz_level in quiz_levels:
            quiz_cat = quiz_level.category
            riddle_category, created = RiddleCategory.objects.get_or_create(
                name=quiz_cat.name,
                defaults={
                    'difficulty': quiz_cat.difficulty,
                    'description': quiz_cat.description,
                    'color': quiz_cat.color,
                    'icon': quiz_cat.icon,
                    'is_active': quiz_cat.is_active,
                }
            )

            if not created:
                updated = False
                for field in ['difficulty', 'description', 'color', 'icon', 'is_active']:
                    quiz_value = getattr(quiz_cat, field)
                    if getattr(riddle_category, field) != quiz_value:
                        setattr(riddle_category, field, quiz_value)
                        updated = True
                if updated:
                    riddle_category.save()

            riddle_level, created = RiddleLevel.objects.get_or_create(
                level_number=quiz_level.level_number,
                defaults={
                    'category': riddle_category,
                    'questions_required': quiz_level.questions_required,
                    'time_limit': quiz_level.time_limit,
                    'unlock_score': quiz_level.unlock_score,
                }
            )

            if not created:
                needs_save = False
                if riddle_level.category != riddle_category:
                    riddle_level.category = riddle_category
                    needs_save = True
                for field in ['questions_required', 'time_limit', 'unlock_score']:
                    quiz_val = getattr(quiz_level, field)
                    if getattr(riddle_level, field) != quiz_val:
                        setattr(riddle_level, field, quiz_val)
                        needs_save = True
                if needs_save:
                    riddle_level.save()

    LEVELS_SYNCED = True

def riddles_game(request):
    """Main riddles game view."""
    return render(request, 'riddles/riddles.html')

# Backwards compatibility for any legacy imports
riddles = riddles_game

def is_riddle_used(question_text, used_riddles, threshold=0.8):
    """
    Check if a riddle is too similar to already used ones.
    Uses simple text similarity to prevent similar riddles.
    """
    question_lower = question_text.lower().strip()
    
    for used_question in used_riddles:
        used_lower = used_question.lower().strip()
        
        # Simple similarity check - if they share many common words
        question_words = set(question_lower.split())
        used_words = set(used_lower.split())
        
        if len(question_words & used_words) / max(len(question_words), 1) > threshold:
            return True
            
        # Check if one is a substring of the other (for very similar riddles)
        if question_lower in used_lower or used_lower in question_lower:
            if len(question_lower) > 20 or len(used_lower) > 20:  # Only for longer texts
                return True
                
    return False

def get_riddle_level(request):
    """Get riddle questions for a specific level, ensuring no repetitions"""
    level_number = int(request.GET.get('level', 1))
    session_id = request.GET.get('session_id', 'anonymous')
    
    sync_riddle_levels_from_quiz()
    
    # Get list of already answered question IDs to exclude
    answered_ids_param = request.GET.get('answered_ids', '')
    answered_ids = []
    if answered_ids_param:
        for raw_id in answered_ids_param.split(','):
            raw_id = raw_id.strip()
            if raw_id.isdigit():
                answered_ids.append(int(raw_id))
    
    try:
        # Filter levels by age-appropriate difficulty
        levels = RiddleLevel.objects.filter(level_number=level_number)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
        level = levels_query.first()
        
        if not level:
            # Fallback to default level if age filtering removes it
            level = RiddleLevel.objects.get(level_number=level_number)
        
        # Filter categories by age-appropriate difficulty
        categories = RiddleCategory.objects.filter(is_active=True)
        categories_query = filter_by_age_appropriate(user, categories, 'difficulty')
        
        # Use age-appropriate category if available
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)
            age_difficulty = get_difficulty_by_age(user_age)
            if age_difficulty:
                categories_query = categories_query.filter(difficulty=age_difficulty)
        
        # If no age-appropriate category, fall back to level's category
        if not categories_query.exists():
            categories_query = RiddleCategory.objects.filter(pk=level.category.pk)
        
        # Get available database questions (excluding answered ones)
        questions_query = RiddleQuestion.objects.filter(
            category__in=categories_query.values_list('pk', flat=True),
            is_active=True
        )
        answer_pool = list(
            RiddleQuestion.objects.filter(is_active=True).values_list('answer', flat=True)
        )
        
        # Exclude already answered questions
        if answered_ids:
            questions_query = questions_query.exclude(id__in=answered_ids)
        
        # Get available database questions with randomization
        available_db_questions = list(questions_query.order_by('?'))
        riddles_needed = level.questions_required
        questions_data = []
        
        current_difficulty = level.category.difficulty
        
        # Get category for AI questions context
        category = categories_query.first()
        topic = category.name if category else "general knowledge"
        
        # Get user age for AI question generation
        user_age = 10  # default
        if user and hasattr(user, 'profile') and user.profile.date_of_birth:
            user_age = get_age_from_birthdate(user.profile.date_of_birth)

        # TRACKING SYSTEM: Get used riddles from cache
        used_riddles_cache_key = get_used_riddles_cache_key(session_id, level_number)
        used_riddles = cache.get(used_riddles_cache_key, [])
        
        # Also track global used riddles for this user/session
        global_used_key = get_global_used_riddles_cache_key(user.id if user else None)
        global_used_riddles = cache.get(global_used_key, [])
        
        # STRATEGY: Use AI riddles first, fallback to database riddles when AI fails
        ai_riddles_count = 0
        db_riddles_count = 0
        max_attempts_per_riddle = 3  # Maximum attempts to generate a unique riddle

        for i in range(riddles_needed):
            riddle_found = False
            attempts = 0
            
            while not riddle_found and attempts < max_attempts_per_riddle:
                attempts += 1
                
                # Try AI riddle first
                try:
                    ai_riddle = generate_ai_riddle(
                        difficulty=current_difficulty,
                        age=user_age,
                        topic=topic,
                        riddle_number=i + 1
                    )
                    
                    # Check if this riddle is too similar to already used ones
                    if is_riddle_used(ai_riddle['question'], used_riddles + global_used_riddles):
                        print(f"AI riddle {i+1} too similar to used ones, attempt {attempts}")
                        continue
                    
                    # Use AI-generated distractors when available
                    ai_distractors = ai_riddle.get('distractors', [])
                    
                    questions_data.append({
                        'id': f"ai_{level_number}_{i}_{random.randint(1000,9999)}",
                        'question_text': ai_riddle['question'],
                        'answer': ai_riddle['answer'],
                        'explanation': ai_riddle['explanation'],
                        'is_ai': True,
                        'options': generate_options(ai_riddle['answer'], answer_pool, ai_distractors),
                        'tip': build_tip(ai_riddle['question'], ai_riddle['answer']),
                        'hint': ai_riddle.get('hint') or build_hint(ai_riddle['answer'])
                    })
                    
                    # Track this riddle as used
                    used_riddles.append(ai_riddle['question'])
                    global_used_riddles.append(ai_riddle['question'])
                    
                    ai_riddles_count += 1
                    riddle_found = True
                    print(f"AI riddle {i+1} generated successfully")
                    
                except Exception as e:
                    print(f"Error generating AI riddle: {e}")
                    break  # Break out of attempts loop for AI
            
            # If AI failed or produced duplicates, try database questions
            if not riddle_found and available_db_questions:
                db_attempts = 0
                while available_db_questions and db_attempts < len(available_db_questions):
                    db_question = available_db_questions.pop(0)
                    db_attempts += 1
                    
                    # Check if this database riddle is too similar to used ones
                    if is_riddle_used(db_question.question_text, used_riddles + global_used_riddles):
                        print(f"DB riddle too similar, trying next...")
                        continue
                    
                    questions_data.append({
                        'id': db_question.id,
                        'question_text': db_question.question_text,
                        'answer': db_question.answer,
                        'explanation': db_question.explanation,
                        'is_ai': False,
                        'options': generate_options(db_question.answer, answer_pool),
                        'tip': build_tip(db_question.question_text, db_question.answer),
                        'hint': build_hint(db_question.answer)
                    })
                    
                    # Track this riddle as used
                    used_riddles.append(db_question.question_text)
                    global_used_riddles.append(db_question.question_text)
                    
                    db_riddles_count += 1
                    riddle_found = True
                    print(f"DB riddle {i+1} used successfully")
                    break
            
            # Last resort: use simple fallback (ensure it's unique)
            if not riddle_found:
                fallback_attempts = 0
                while fallback_attempts < 3:  # Try up to 3 different fallbacks
                    fallback_riddle = create_unique_fallback_riddle(level_number, i + fallback_attempts, current_difficulty, topic)
                    fallback_attempts += 1
                    
                    if not is_riddle_used(fallback_riddle['question'], used_riddles + global_used_riddles):
                        questions_data.append({
                            'id': f"fallback_{level_number}_{i}_{fallback_attempts}",
                            'question_text': fallback_riddle['question'],
                            'answer': fallback_riddle['answer'],
                            'explanation': fallback_riddle['explanation'],
                            'is_ai': False,
                            'options': generate_options(fallback_riddle['answer'], answer_pool),
                            'tip': build_tip(fallback_riddle['question'], fallback_riddle['answer']),
                            'hint': fallback_riddle.get('hint') or build_hint(fallback_riddle['answer'])
                        })
                        
                        # Track this riddle as used
                        used_riddles.append(fallback_riddle['question'])
                        global_used_riddles.append(fallback_riddle['question'])
                        
                        riddle_found = True
                        print(f"Fallback riddle {i+1} used successfully")
                        break
        
        # Update cache with used riddles (store for 1 hour)
        cache.set(used_riddles_cache_key, used_riddles, 3600)
        cache.set(global_used_key, global_used_riddles, 3600)
        
        # Shuffle the final riddles
        random.shuffle(questions_data)
        
        level_data = {
            'level_number': level.level_number,
            'category': level.category.name,
            'difficulty': current_difficulty,
            'color': level.category.color,
            'icon': level.category.icon,
            'time_limit': level.time_limit,
            'riddles_required': level.questions_required,
            'questions': questions_data,
            'ai_riddles_count': ai_riddles_count,
            'db_riddles_count': db_riddles_count,
            'session_id': session_id  # Return session_id for client to use
        }
        
        print(f"Level {level_number}: {db_riddles_count} DB riddles, {ai_riddles_count} AI riddles, {len(questions_data)} total unique riddles")
        
        return JsonResponse(level_data)
        
    except RiddleLevel.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def start_riddle_session(request):
    """Start a new riddle game session and initialize tracking"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        player_name = data.get('player_name', 'Player')
        
        user = request.user if request.user.is_authenticated else None
        
        session = RiddleGameSession.objects.create(
            session_id=session_id,
            player_name=player_name,
            user=user,
            current_level=1,
            is_active=True
        )
        
        # Initialize global used riddles cache for this session
        global_used_key = get_global_used_riddles_cache_key(user.id if user else None)
        cache.set(global_used_key, [], 3600)  # 1 hour expiration
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.session_id,
            'message': 'Riddle game session started'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def clear_used_riddles(request):
    """Clear used riddles cache for a session (for testing or session reset)"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level_number = data.get('level_number')
        user = request.user if request.user.is_authenticated else None
        
        if session_id and level_number:
            cache_key = get_used_riddles_cache_key(session_id, level_number)
            cache.delete(cache_key)
        
        # Also clear global used riddles
        global_key = get_global_used_riddles_cache_key(user.id if user else None)
        cache.delete(global_key)
        
        return JsonResponse({'status': 'success', 'message': 'Used riddles cleared'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ... (keep the other functions: update_riddle_progress, get_next_riddle_level, get_riddle_categories, get_next_riddle unchanged)
@csrf_exempt
@require_http_methods(["POST"])
def update_riddle_progress(request):
    """Update riddle game progress for a session and user."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        level = data.get('level')
        score = data.get('score')
        questions_answered = data.get('questions_answered')
        correct_answers = data.get('correct_answers')
        perfect_streak = data.get('perfect_streak', 0)
        time_spent = data.get('time_spent')

        session = RiddleGameSession.objects.get(session_id=session_id)
        session.current_level = level
        session.total_score = score
        session.questions_answered = questions_answered
        session.correct_answers = correct_answers
        session.perfect_streak = perfect_streak
        session.time_spent = time_spent
        session.save()

        if session.user:
            progress, _ = UserRiddleProgress.objects.get_or_create(user=session.user)
            if level > progress.highest_level:
                progress.highest_level = level
            progress.total_score += score
            progress.total_questions += questions_answered
            progress.correct_answers += correct_answers
            if questions_answered and correct_answers == questions_answered:
                progress.perfect_riddles += 1
            progress.games_played += 1
            progress.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def get_next_riddle_level(request):
    """Return metadata for the next riddle level."""
    current_level = int(request.GET.get('current_level', 1))
    next_level = current_level + 1

    try:
        levels = RiddleLevel.objects.filter(level_number=next_level)
        user = request.user if request.user.is_authenticated else None
        levels_query = filter_by_age_appropriate(user, levels, 'category__difficulty')
        level = levels_query.first()

        if not level:
            level = RiddleLevel.objects.get(level_number=next_level)

        return JsonResponse({
            'level_number': level.level_number,
            'category': level.category.name,
            'difficulty': level.category.difficulty,
            'unlock_score': level.unlock_score
        })
    except RiddleLevel.DoesNotExist:
        return JsonResponse({'error': 'No more levels'}, status=404)


def get_riddle_categories(request):
    """List active riddle categories filtered by age difficulty."""
    categories = RiddleCategory.objects.filter(is_active=True)
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
            'riddle_count': cat.questions.filter(is_active=True).count()
        }
        for cat in categories_query
    ]
    return JsonResponse({'categories': categories_data})


@csrf_exempt
def get_next_riddle(request):
    """Return a single AI-generated riddle (quick play)."""
    user = request.user
    difficulty = "easy"

    riddle_data = generate_ai_riddle(
        difficulty=difficulty,
        age=user.profile.age if hasattr(user, "profile") else 10,
        topic="riddles"
    )

    return JsonResponse(riddle_data, safe=False)