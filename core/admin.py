from django.contrib import admin
from .models import *

# ============================================
# WORD CAPTURE GAME ADMIN
# ============================================

@admin.register(CapturePartOfSpeech)
class CapturePartOfSpeechAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'hint_text']
    search_fields = ['name', 'description']


@admin.register(CaptureWord)
class CaptureWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'part_of_speech', 'difficulty', 'hint']
    list_filter = ['part_of_speech', 'difficulty']
    search_fields = ['word', 'hint']
    ordering = ['difficulty', 'part_of_speech', 'word']


@admin.register(CaptureGameSession)
class CaptureGameSessionAdmin(admin.ModelAdmin):
    list_display = ['player_name', 'score', 'level_reached', 'rounds_completed', 'words_captured', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['player_name']
    ordering = ['-score', '-created_at']
    readonly_fields = ['created_at']


from django.contrib import admin
from .models import WordSearchLevel, WordSearchCategory, WordSearchPuzzle, WordSearchGameSession, UserWordSearchProgress

@admin.register(WordSearchLevel)
class WordSearchLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'difficulty', 'grid_size', 'word_count', 'time_limit']
    list_editable = ['grid_size', 'word_count', 'time_limit']
    ordering = ['level_number']

@admin.register(WordSearchCategory)
class WordSearchCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(WordSearchPuzzle)
class WordSearchPuzzleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'is_active']
    list_filter = ['category', 'level', 'is_active']
    search_fields = ['title', 'words']
    list_editable = ['is_active']

@admin.register(WordSearchGameSession)
class WordSearchGameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'player_name', 'current_level', 'total_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserWordSearchProgress)
class UserWordSearchProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'highest_level', 'total_score', 'total_words_found', 'perfect_puzzles']
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from .models import GameLevel, GameEmoji, GameSession, UserGameProgress, UserProfile

@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'rows', 'columns', 'preview_time']
    ordering = ['level_number']

@admin.register(GameEmoji)
class GameEmojiAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'category', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'level', 'moves', 'matched_pairs', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']

@admin.register(UserGameProgress)
class UserGameProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'highest_level', 'total_moves', 'games_completed']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_completed', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


from django.contrib import admin
from .models import SentenceBuilderLevel, SentenceBuilderSentence, SentenceBuilderGameSession, UserSentenceProgress

@admin.register(SentenceBuilderLevel)
class SentenceBuilderLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'difficulty', 'sentences_required', 'time_limit', 'points_per_sentence']
    list_editable = ['sentences_required', 'time_limit', 'points_per_sentence']
    ordering = ['level_number']

@admin.register(SentenceBuilderSentence)
class SentenceBuilderSentenceAdmin(admin.ModelAdmin):
    list_display = ['sentence', 'level', 'word_count', 'is_active']
    list_filter = ['level', 'is_active', 'level__difficulty']
    search_fields = ['sentence', 'hint']
    list_editable = ['is_active']

@admin.register(SentenceBuilderGameSession)
class SentenceBuilderGameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'player_name', 'current_level', 'total_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserSentenceProgress)
class UserSentenceProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'highest_level', 'total_score', 'total_sentences', 'games_played']
    readonly_fields = ['created_at', 'updated_at']


from django.contrib import admin
from .models import MathGameLevel, MathGameProblem, MathGameSession, UserMathProgress

@admin.register(MathGameLevel)
class MathGameLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'difficulty', 'operations', 'number_range_min', 'number_range_max', 'problems_required']
    list_editable = ['problems_required', 'number_range_min', 'number_range_max']
    ordering = ['level_number']

@admin.register(MathGameProblem)
class MathGameProblemAdmin(admin.ModelAdmin):
    list_display = ['problem_text', 'correct_answer', 'operation', 'level', 'is_active']
    list_filter = ['level', 'operation', 'is_active']
    search_fields = ['problem_text']
    list_editable = ['is_active']

@admin.register(MathGameSession)
class MathGameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'player_name', 'current_level', 'total_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserMathProgress)
class UserMathProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'highest_level', 'total_score', 'total_problems', 'perfect_streaks', 'games_played']
    readonly_fields = ['created_at', 'updated_at']


from django.contrib import admin
from .models import QuizCategory, QuizQuestion, QuizLevel, QuizGameSession, UserQuizProgress

@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'icon', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'category', 'correct_option', 'points', 'is_active']
    list_filter = ['category', 'is_active', 'category__difficulty']
    search_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d']
    list_editable = ['is_active', 'points']

@admin.register(QuizLevel)
class QuizLevelAdmin(admin.ModelAdmin):
    list_display = ['level_number', 'category', 'questions_required', 'time_limit']
    list_editable = ['questions_required', 'time_limit']
    ordering = ['level_number']

@admin.register(QuizGameSession)
class QuizGameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'player_name', 'current_level', 'total_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserQuizProgress)
class UserQuizProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'highest_level', 'total_score', 'accuracy_rate', 'games_played']
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from .models import (
    RiddleCategory,
    RiddleQuestion,
    RiddleLevel,
    RiddleGameSession,
    UserRiddleProgress
)

admin.site.register(RiddleCategory)
admin.site.register(RiddleQuestion)
admin.site.register(RiddleLevel)
admin.site.register(RiddleGameSession)
admin.site.register(UserRiddleProgress)
