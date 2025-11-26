from django.urls import path
from . import views
from .score_views import save_score, scores
from . import new_views
from . import color_splash_view
from . import sentence_builder
from . import math_game
from . import quiz_game
from . import riddles_game
from . import ai_question_generator

urlpatterns = [
    # Authentication URLs
    path('', views.splash_screen, name='splash_screen'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile-setup/', views.profile_setup_view, name='profile_setup'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),

    # Word Search URL/
    path('word-search/', views.word_search_game, name='word_search'),
    path('word-search/<int:category_id>/', views.word_search_game, name='word_search_category'),

    
    # Word Capture Game
    path('capture-words/', views.capture_words, name='capture_words'),
    path('api/capture/get-words/', views.get_capture_words, name='get_capture_words'),
    path('api/capture/get-mixed-words/', views.get_mixed_capture_words, name='get_mixed_capture_words'),
    path('api/capture/save-session/', views.save_capture_session, name='save_capture_session'),
    path('api/capture/leaderboard/', views.get_capture_leaderboard, name='capture_leaderboard'),
    
    # Word Search Game
    path('words-search/', views.words_search, name='words_search'),
    path('api/word-search/level/', views.get_word_search_level, name='get_word_search_level'),
    path('api/word-search/start-session/', views.start_word_search_session, name='start_word_search_session'),
    path('api/word-search/update-progress/', views.update_word_search_progress, name='update_word_search_progress'),
    path('api/word-search/next-level/', views.get_next_word_search_level, name='get_next_word_search_level'),

    # Tracing Letters Game
    path('tracing-letters/', views.tracing_letters, name='tracing_letters'),
    path('match-game/', views.match_game, name='match_game'),


    # Profile URL
    path('profile/', views.profile_view, name='profile'),
    path('artificial-intelligence/', views.artificial_intelligence, name='artificial_intelligence'),
    path('games-page/', views.games_page, name='games_page'),

    # Quiz Game
    path('quizes/', quiz_game.quizes, name='quizes'),
    path('api/quizes/level/', quiz_game.get_quiz_level, name='get_quiz_level'),
    path('api/quizes/start-session/', quiz_game.start_quiz_session, name='start_quiz_session'),
    path('api/quizes/update-progress/', quiz_game.update_quiz_progress, name='update_quiz_progress'),
    path('api/quizes/next-level/', quiz_game.get_next_quiz_level, name='get_next_quiz_level'),
    path('api/quizes/categories/', quiz_game.get_quiz_categories, name='get_quiz_categories'),

    # Riddles Game URLs
    path('riddles/', riddles_game.riddles_game, name='riddles'),
    path('api/riddles/level/', riddles_game.get_riddle_level, name='get_riddle_level'),
    path('api/riddles/start/', riddles_game.start_riddle_session, name='start_riddle_session'),
    path('api/riddles/update/', riddles_game.update_riddle_progress, name='update_riddle_progress'),
    path('api/riddles/next-level/', riddles_game.get_next_riddle_level, name='get_next_riddle_level'),
    path('api/riddles/categories/', riddles_game.get_riddle_categories, name='get_riddle_categories'),
    path('api/riddles/next/', riddles_game.get_next_riddle, name='get_next_riddle'),
    
    # Math Game
    path('math-game/', math_game.math_game, name='math_game'),
    path('api/math-game/level/', math_game.get_math_level, name='get_math_level'),
    path('api/math-game/start-session/', math_game.start_math_session, name='start_math_session'),
    path('api/math-game/update-progress/', math_game.update_math_progress, name='update_math_progress'),
    path('api/math-game/next-level/', math_game.get_next_math_level, name='get_next_math_level'),

    
    # sentence builder
    path('sentence-builder/', sentence_builder.sentence_builder, name='sentence_builder'),
    path('api/sentence-builder/level/', sentence_builder.get_level_sentences, name='get_level_sentences'),
    path('api/sentence-builder/start-session/', sentence_builder.start_sentence_session, name='start_sentence_session'),
    path('api/sentence-builder/update-progress/', sentence_builder.update_sentence_progress, name='update_sentence_progress'),
    path('api/sentence-builder/next-level/', sentence_builder.get_next_level, name='get_next_level'),


    # ... your existing urls ...
    path('save_score/', save_score, name='save_score'),
    path('scores/', scores, name='scores'),


    # memory match
    path('memory-game/', new_views.memory_game, name='game'),
    path('api/level/', new_views.get_level_data, name='get_level'),
    path('api/save-game/', new_views.save_game_state, name='save_game'),
    path('api/load-game/', new_views.load_game_state, name='load_game'),
    path('api/complete-level/', new_views.complete_level, name='complete_level'),


    # color splash
    path('color-splash/', color_splash_view.color_splash_game, name='color_game'),
    path('api/color-level/', color_splash_view.get_color_level_data, name='get_color_level'),
    path('api/save-color-game/', color_splash_view.save_color_game_state, name='save_color_game'),
    path('api/load-color-game/', color_splash_view.load_color_game_state, name='load_color_game'),
    path('api/complete-color-level/', color_splash_view.complete_color_level, name='complete_color_level'),

    # ai question generator
    path('api/get-next-question/', quiz_game.get_next_question, name='get_next_question'),
]