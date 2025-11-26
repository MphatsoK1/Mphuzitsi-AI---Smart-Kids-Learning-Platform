from django.db import models
import random
import string
import json
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    preset_avatar = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        """Return the avatar URL - either custom or preset"""
        if self.avatar:
            return self.avatar.url
        elif self.preset_avatar:
            # Avatars are stored as .jpg files
            return f'/static/avatars/{self.preset_avatar}.jpg'
        # Default fallback - use first available avatar or a placeholder
        return '/static/avatars/58509039_9439767.jpg'
    
    from datetime import date

    def age(self):
        """Calculate the user's age based on date_of_birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return (
            today.year - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )


# Signal to create profile automatically when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class GameScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    game_name = models.CharField(max_length=100)
    score = models.IntegerField()
    milestone = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game_name} - {self.score}" 

# ============================================
# WORD CAPTURE GAME MODELS
# ============================================

class CapturePartOfSpeech(models.Model):
    """Stores different parts of speech categories for Word Capture game"""
    TYPES = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('pronoun', 'Pronoun'),
    ]
    
    name = models.CharField(max_length=20, choices=TYPES, unique=True)
    description = models.TextField(help_text="Kid-friendly description")
    hint_text = models.CharField(max_length=200, help_text="Hint for kids")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Capture Part of Speech"
        verbose_name_plural = "Capture Parts of Speech"
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class CaptureWord(models.Model):
    """Stores words for the Word Capture game"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy (3-6 years)'),
        ('medium', 'Medium (7-9 years)'),
        ('hard', 'Hard (10-12 years)'),
    ]
    
    word = models.CharField(max_length=20)
    part_of_speech = models.ForeignKey(
        CapturePartOfSpeech, 
        on_delete=models.CASCADE, 
        related_name='capture_words'
    )
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    hint = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Capture Word"
        verbose_name_plural = "Capture Words"
        ordering = ['word']
        unique_together = ['word', 'part_of_speech', 'difficulty']
    
    def __str__(self):
        return f"{self.word} ({self.get_difficulty_display()} - {self.part_of_speech})"


class CaptureGameSession(models.Model):
    """Tracks game sessions for Word Capture game"""
    player_name = models.CharField(max_length=100, default='Player')
    score = models.IntegerField(default=0)
    level_reached = models.IntegerField(default=1)
    rounds_completed = models.IntegerField(default=0)
    words_captured = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)  # seconds
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Capture Game Session"
        verbose_name_plural = "Capture Game Sessions"
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.player_name} - Level {self.level_reached} - {self.score} pts"

# ============================================
# WORD SEARCH GAME MODELS - ENHANCED
# ============================================

class WordSearchLevel(models.Model):  # REMOVE THIS DUPLICATE
    """Level configurations for Word Search game"""
    level_number = models.IntegerField(unique=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'), 
        ('hard', 'Hard'),
        ('expert', 'Expert')
    ])
    grid_size = models.IntegerField(default=8)
    word_count = models.IntegerField(default=8)
    time_limit = models.IntegerField(default=180)  # seconds
    points_per_word = models.IntegerField(default=10)
    unlock_score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.difficulty}"

class WordSearchCategory(models.Model):  # REMOVE THIS DUPLICATE
    """Categories for word search puzzles"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color for UI
    icon = models.CharField(max_length=50, default='🔍')  # Emoji icon
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Word Search Category"
        verbose_name_plural = "Word Search Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class WordSearchPuzzle(models.Model):  # REMOVE THIS DUPLICATE
    """Pre-generated word search puzzles"""
    title = models.CharField(max_length=200)
    category = models.ForeignKey(WordSearchCategory, on_delete=models.CASCADE, related_name='puzzles')
    level = models.ForeignKey(WordSearchLevel, on_delete=models.CASCADE, related_name='puzzles')
    words = models.JSONField()  # List of words for the puzzle
    grid_data = models.JSONField()  # Pre-generated grid data
    word_positions = models.JSONField()  # Word positions in the grid
    hints = models.JSONField(default=dict)  # Word hints
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['level__level_number', 'title']
    
    def __str__(self):
        return f"{self.title} - Level {self.level.level_number}"

class WordSearchGameSession(models.Model):  # REMOVE THIS DUPLICATE
    """Game sessions for Word Search game"""
    session_id = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    words_found = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    perfect_puzzles = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Word Search Game Session"
        verbose_name_plural = "Word Search Game Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.current_level}"

class UserWordSearchProgress(models.Model):  # REMOVE THIS DUPLICATE
    """User progress tracking for Word Search"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_search_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    total_words_found = models.IntegerField(default=0)
    perfect_puzzles = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Word Search Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"

# ============================================
# MATCHING PAIRS GAME MODELS
# ============================================

class GameLevel(models.Model):
    """Model to store game level configurations"""
    level_number = models.IntegerField(unique=True)
    rows = models.IntegerField()
    columns = models.IntegerField()
    preview_time = models.IntegerField(default=2000)
    required_pairs = models.IntegerField(default=2)
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} ({self.rows}x{self.columns})"

class GameEmoji(models.Model):
    """Model to store available emojis for the game"""
    emoji = models.CharField(max_length=10)
    category = models.CharField(max_length=50, default='general')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.emoji

class GameSession(models.Model):
    """Model to store active game sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    level = models.IntegerField(default=1)
    moves = models.IntegerField(default=0)
    matched_pairs = models.IntegerField(default=0)
    cards_data = models.JSONField(default=dict)  # Store card state
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.level}"

class UserGameProgress(models.Model):
    """Model to store user's game progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_progress')
    highest_level = models.IntegerField(default=1)
    total_moves = models.IntegerField(default=0)
    games_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Game Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"

# ============================================
# COLOR SPLASH GAME MODELS
# ============================================

class ColorSplashLevel(models.Model):
    """Model to store Color Splash level configurations"""
    level_number = models.IntegerField(unique=True)
    grid_size = models.IntegerField(default=4)  # 2x2, 3x3, 4x4, etc.
    required_matches = models.IntegerField(default=4)  # How many to complete
    time_limit = models.IntegerField(default=180)  # seconds
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.grid_size}x{self.grid_size}"

class FruitColor(models.Model):
    """Model to store fruits and their colors"""
    name = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10)
    color = models.CharField(max_length=50)  # e.g., 'red', 'yellow', 'orange'
    hex_color = models.CharField(max_length=7, default='#000000')  # For display
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Fruit Colors"
    
    def __str__(self):
        return f"{self.name} {self.emoji} - {self.color}"

class ColorPalette(models.Model):
    """Model to store available colors for painting"""
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.name} ({self.hex_code})"

class ColorSplashSession(models.Model):
    """Model to store active Color Splash game sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    level = models.IntegerField(default=1)
    score = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    time_elapsed = models.IntegerField(default=0)  # seconds
    game_data = models.JSONField(default=dict)  # Store current game state
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.level}"

class UserColorProgress(models.Model):
    """Model to store user's Color Splash progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='color_splash_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    perfect_matches = models.IntegerField(default=0)  # Matches without hints
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Color Splash Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"

# ============================================
# SENTENCE BUILDER GAME MODELS - ENHANCED
# ============================================

class SentenceBuilderLevel(models.Model):
    """Level configurations for Sentence Builder game"""
    level_number = models.IntegerField(unique=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'), 
        ('hard', 'Hard'),
        ('expert', 'Expert')
    ])
    sentences_required = models.IntegerField(default=3)
    time_limit = models.IntegerField(default=180)  # seconds
    points_per_sentence = models.IntegerField(default=10)
    unlock_score = models.IntegerField(default=0)  # Score needed to unlock this level
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.difficulty}"

class SentenceBuilderSentence(models.Model):
    """Sentences for Sentence Builder game"""
    sentence = models.TextField(help_text="The complete correct sentence")
    level = models.ForeignKey(
        SentenceBuilderLevel, 
        on_delete=models.CASCADE, 
        related_name='sentences'
    )
    hint = models.TextField(blank=True, help_text="Optional hint for the sentence")
    word_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sentence Builder Sentence"
        verbose_name_plural = "Sentence Builder Sentences"
        ordering = ['level__level_number', 'word_count']
    
    def __str__(self):
        return f"{self.sentence[:50]}..." if len(self.sentence) > 50 else self.sentence
    
    def save(self, *args, **kwargs):
        self.word_count = len(self.sentence.split())
        super().save(*args, **kwargs)
    
    def get_scrambled_words(self):
        """Return the sentence words in scrambled order"""
        words = self.sentence.split()
        scrambled = words.copy()
        import random
        random.shuffle(scrambled)
        return scrambled

class SentenceBuilderGameSession(models.Model):
    """Game sessions for Sentence Builder game"""
    session_id = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    sentences_completed = models.IntegerField(default=0)
    perfect_sentences = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sentence Builder Game Session"
        verbose_name_plural = "Sentence Builder Game Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.current_level}"
    
    def accuracy_rate(self):
        if self.total_attempts == 0:
            return 0
        return round((self.correct_attempts / self.total_attempts) * 100, 1)

class UserSentenceProgress(models.Model):
    """User progress tracking for Sentence Builder"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentence_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    total_sentences = models.IntegerField(default=0)
    perfect_sentences = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Sentence Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"
    

# ============================================
# MATH GAME MODELS
# ============================================

class MathGameLevel(models.Model):
    """Level configurations for Math Game"""
    level_number = models.IntegerField(unique=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'), 
        ('hard', 'Hard'),
        ('expert', 'Expert')
    ])
    operations = models.JSONField(default=list)  # ['+', '-', '×', '÷']
    number_range_min = models.IntegerField(default=1)
    number_range_max = models.IntegerField(default=10)
    problems_required = models.IntegerField(default=10)
    time_limit = models.IntegerField(default=180)  # seconds
    points_per_problem = models.IntegerField(default=10)
    unlock_score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.difficulty}"

class MathGameProblem(models.Model):
    """Math problems for the game"""
    problem_text = models.CharField(max_length=100)
    correct_answer = models.IntegerField()
    operation = models.CharField(max_length=5)
    level = models.ForeignKey(MathGameLevel, on_delete=models.CASCADE, related_name='problems')
    hint = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['level__level_number']
    
    def __str__(self):
        return f"{self.problem_text} = {self.correct_answer}"

class MathGameSession(models.Model):
    """Game sessions for Math Game"""
    session_id = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    problems_completed = models.IntegerField(default=0)
    perfect_streak = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Math Game Session"
        verbose_name_plural = "Math Game Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.current_level}"

class UserMathProgress(models.Model):
    """User progress tracking for Math Game"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='math_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    total_problems = models.IntegerField(default=0)
    perfect_streaks = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Math Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"
    

# ============================================
# QUIZ GAME MODELS
# ============================================

class QuizCategory(models.Model):
    """Categories for quiz questions"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'), 
        ('hard', 'Hard'),
        ('expert', 'Expert')
    ]
    
    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color for UI
    icon = models.CharField(max_length=50, default='🧠')  # Emoji icon
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Quiz Category"
        verbose_name_plural = "Quiz Categories"
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"

class QuizQuestion(models.Model):
    """Quiz questions and answers"""
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'), 
        ('C', 'C'),
        ('D', 'D')
    ])
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category__difficulty', 'points']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."
    
    def get_options(self):
        """Return options as a list"""
        return [
            {'letter': 'A', 'text': self.option_a},
            {'letter': 'B', 'text': self.option_b},
            {'letter': 'C', 'text': self.option_c},
            {'letter': 'D', 'text': self.option_d}
        ]
    
    def get_correct_answer(self):
        """Get the correct answer text"""
        options = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }
        return options.get(self.correct_option)

class QuizLevel(models.Model):
    """Level configurations for Quiz Game"""
    level_number = models.IntegerField(unique=True)
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    questions_required = models.IntegerField(default=5)
    time_limit = models.IntegerField(default=300)  # seconds
    unlock_score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.category.name}"

class QuizGameSession(models.Model):
    """Game sessions for Quiz Game"""
    session_id = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    perfect_streak = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Quiz Game Session"
        verbose_name_plural = "Quiz Game Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.current_level}"
    
    def accuracy_rate(self):
        if self.questions_answered == 0:
            return 0
        return round((self.correct_answers / self.questions_answered) * 100, 1)

class UserQuizProgress(models.Model):
    """User progress tracking for Quiz Game"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    perfect_quizzes = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Quiz Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"
    
    def accuracy_rate(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 1)


# ============================================
# Riddle GAME MODELS
# ============================================

class RiddleCategory(models.Model):
    """Categories for quiz questions"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'), 
        ('hard', 'Hard'),
        ('expert', 'Expert')
    ]
    
    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color for UI
    icon = models.CharField(max_length=50, default='🧠')  # Emoji icon
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Riddle Category"
        verbose_name_plural = "Riddle Categories"
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"

class RiddleQuestion(models.Model):
    """Riddle questions and answers"""
    category = models.ForeignKey(RiddleCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer = models.TextField()
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category__difficulty']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."
    

class RiddleLevel(models.Model):
    """Level configurations for Quiz Game"""
    level_number = models.IntegerField(unique=True)
    category = models.ForeignKey(RiddleCategory, on_delete=models.CASCADE)
    questions_required = models.IntegerField(default=5)
    time_limit = models.IntegerField(default=300)  # seconds
    unlock_score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['level_number']
    
    def __str__(self):
        return f"Level {self.level_number} - {self.category.name}"

class RiddleGameSession(models.Model):
    """Game sessions for Quiz Game"""
    session_id = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    perfect_streak = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Riddle Game Session"
        verbose_name_plural = "Riddle Game Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - Level {self.current_level}"
    
    def accuracy_rate(self):
        if self.questions_answered == 0:
            return 0
        return round((self.correct_answers / self.questions_answered) * 100, 1)

class UserRiddleProgress(models.Model):
    """User progress tracking for Riddle Game"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='riddle_progress')
    highest_level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    perfect_riddles = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Riddle Progress"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.highest_level}"
    
    def accuracy_rate(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 1)