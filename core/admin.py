# from django.contrib import admin
# from .models import *

# # Register your models here.
# from django.contrib import admin
# from .models import *

# @admin.register(WordCategory)
# class WordCategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'icon', 'is_active', 'created_at']
#     list_filter = ['is_active']
#     search_fields = ['name']

# @admin.register(WordItem)
# class WordItemAdmin(admin.ModelAdmin):
#     list_display = ['word', 'category', 'difficulty_level', 'part_of_speech', 'is_active']
#     list_filter = ['category', 'difficulty_level', 'is_active']
#     search_fields = ['word', 'definition']

# @admin.register(WordSearchGame)
# class WordSearchGameAdmin(admin.ModelAdmin):
#     list_display = ['id', 'category', 'difficulty', 'learning_mode', 'completed', 'created_at']
#     list_filter = ['difficulty', 'learning_mode', 'completed']
#     search_fields = ['category__name']

# # @admin.register(GameSession)
# # class GameSessionAdmin(admin.ModelAdmin):
# #     list_display = ['session_id', 'game', 'score', 'completed', 'start_time']
# #     list_filter = ['completed']
# #     search_fields = ['session_id']

# @admin.register(UserWordProgress)
# class UserWordProgressAdmin(admin.ModelAdmin):
#     list_display = ['user_identifier', 'word', 'times_correct', 'times_attempted', 'accuracy']
#     list_filter = ['word__category']
#     search_fields = ['user_identifier', 'word__word']

# # auth/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
# from .models import UserProfile

# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'
#     fields = ('preset_avatar', 'avatar', 'profile_completed', 'created_at', 'updated_at')
#     readonly_fields = ('created_at', 'updated_at')

# class UserAdmin(BaseUserAdmin):
#     inlines = (UserProfileInline,)
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_profile_status')
#     list_select_related = ('profile',)

#     def get_profile_status(self, instance):
#         return '✓ Complete' if instance.profile.profile_completed else '✗ Incomplete'
#     get_profile_status.short_description = 'Profile Status'

#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super(UserAdmin, self).get_inline_instances(request, obj)

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'profile_completed', 'preset_avatar', 'has_custom_avatar', 'created_at']
#     list_filter = ['profile_completed', 'created_at', 'preset_avatar']
#     search_fields = ['user__username', 'user__email']
#     readonly_fields = ['created_at', 'updated_at', 'get_avatar_preview']
    
#     fieldsets = (
#         ('User Information', {
#             'fields': ('user',)
#         }),
#         ('Avatar Settings', {
#             'fields': ('preset_avatar', 'avatar', 'get_avatar_preview')
#         }),
#         ('Status', {
#             'fields': ('profile_completed', 'created_at', 'updated_at')
#         }),
#     )

#     def has_custom_avatar(self, obj):
#         return bool(obj.avatar)
#     has_custom_avatar.boolean = True
#     has_custom_avatar.short_description = 'Custom Avatar'

#     def get_avatar_preview(self, obj):
#         from django.utils.html import format_html
#         if obj.avatar or obj.preset_avatar:
#             return format_html(
#                 '<img src="{}" style="width: 100px; height: 100px; border-radius: 50%; border: 2px solid #667eea;" />',
#                 obj.get_avatar_url()
#             )
#         return 'No avatar set'
#     get_avatar_preview.short_description = 'Avatar Preview'


# from django.contrib import admin
# from .models import *

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category_type', 'icon', 'is_active', 'created_at']
#     list_filter = ['category_type', 'is_active']
#     search_fields = ['name']

# @admin.register(LearningItem)
# class LearningItemAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'order', 'is_active']
#     list_filter = ['category', 'is_active']
#     search_fields = ['name']

# @admin.register(PhonicsItem)
# class PhonicsItemAdmin(admin.ModelAdmin):
#     list_display = ['letter', 'order', 'is_active']
#     list_filter = ['is_active']
#     search_fields = ['letter']

# # @admin.register(GameSession)
# # class GameSessionAdmin(admin.ModelAdmin):
# #     list_display = ['session_id', 'category', 'score', 'completed', 'time_taken', 'created_at']
# #     list_filter = ['category', 'completed']
# #     search_fields = ['session_id']

# @admin.register(UserProgress)
# class UserProgressAdmin(admin.ModelAdmin):
#     list_display = ['user_identifier', 'category', 'total_score', 'games_played', 'levels_completed', 'updated_at']
#     list_filter = ['category']
#     search_fields = ['user_identifier']

# @admin.register(TaskSet)
# class TaskSetAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'items_per_set', 'order', 'is_active']
#     list_filter = ['category', 'is_active']
#     search_fields = ['name']

# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


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