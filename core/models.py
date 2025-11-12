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
            return f'/static/avatars/{self.preset_avatar}.png'
        return '/static/avatars/default.png'

# Signal to create profile automatically when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()






# from django.db import models
from django.contrib.auth.models import User

class GameScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    game_name = models.CharField(max_length=100)
    score = models.IntegerField()
    milestone = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game_name} - {self.score}"





# # Word Search Models
# class WordCategory(models.Model):
#     """Categories for organizing words (Animals, Colors, Numbers, Phonics, etc.)"""
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     icon = models.CharField(max_length=10, default='📚')
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name_plural = "Word categories"
    
#     def __str__(self):
#         return self.name

# class WordItem(models.Model):
#     """Store words for word search games"""
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ]
    
#     category = models.ForeignKey(WordCategory, on_delete=models.CASCADE, related_name='words')
#     word = models.CharField(max_length=50)
#     definition = models.TextField(blank=True)
#     part_of_speech = models.CharField(max_length=20, blank=True)
#     difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
#     phonetic_spelling = models.CharField(max_length=100, blank=True)
#     example_sentence = models.TextField(blank=True)
#     image = models.ImageField(upload_to='word_images/', blank=True, null=True)
#     audio = models.FileField(upload_to='word_audio/', blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['word']
#         unique_together = ['category', 'word']
    
#     def __str__(self):
#         return f"{self.word} ({self.category.name})"

# class WordSearchGame(models.Model):
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ]
    
#     LEARNING_MODE_CHOICES = [
#         ('vocabulary', 'Vocabulary'),
#         ('spelling', 'Spelling'),
#         ('phonics', 'Phonics'),
#     ]
    
#     category = models.ForeignKey(WordCategory, on_delete=models.CASCADE, null=True, blank=True)
#     grid_size = models.IntegerField(default=10)
#     words_data = models.JSONField(default=list)  # Stores words and their positions
#     grid = models.JSONField(default=list)  # Stores the letter grid
#     difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
#     learning_mode = models.CharField(max_length=15, choices=LEARNING_MODE_CHOICES, default='vocabulary')
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed = models.BooleanField(default=False)
#     score = models.IntegerField(default=0)
    
#     def __str__(self):
#         return f"WordSearch {self.id} - {self.difficulty} - {self.learning_mode}"
    
#     def get_words_from_category(self, count=8):
#         """Get random words from the category"""
#         if self.category:
#             words = list(WordItem.objects.filter(
#                 category=self.category, 
#                 is_active=True,
#                 difficulty_level=self.difficulty
#             )[:count])
#             if len(words) >= count:
#                 return [word.word.upper() for word in words]
        
#         # Fallback words if no category or not enough words
#         fallback_words = {
#             'easy': ['CAT', 'DOG', 'SUN', 'MOON', 'STAR', 'TREE', 'FISH', 'BIRD'],
#             'medium': ['PYTHON', 'DJANGO', 'CODE', 'GAME', 'LEARN', 'FUN', 'APP', 'WEB'],
#             'hard': ['PROGRAMMING', 'ALGORITHM', 'DATABASE', 'FRAMEWORK', 'FUNCTION', 'VARIABLE']
#         }
#         return fallback_words.get(self.difficulty, fallback_words['medium'])[:count]
    
#     def generate_grid(self, words=None, allow_crossing=True):
#         """Generate a word search grid with given words"""
#         if not words:
#             words = self.get_words_from_category()
            
#         size = self.grid_size
#         grid = [['' for _ in range(size)] for _ in range(size)]
#         placed_words = []
        
#         # All 8 possible directions
#         directions = [
#             (0, 1),   # right
#             (1, 0),   # down
#             (1, 1),   # diagonal down-right
#             (1, -1),  # diagonal down-left
#             (0, -1),  # left
#             (-1, 0),  # up
#             (-1, -1), # diagonal up-left
#             (-1, 1)   # diagonal up-right
#         ]
        
#         # Sort words by length (longest first for better placement)
#         words = sorted(words, key=len, reverse=True)
        
#         for word in words:
#             word = word.upper().replace(' ', '')
#             if len(word) > size:
#                 continue  # Skip words that are too long
                
#             placed = False
#             attempts = 0
            
#             while not placed and attempts < 100:
#                 direction = random.choice(directions)
#                 dx, dy = direction
                
#                 # Calculate maximum starting position
#                 if dx > 0:
#                     max_start_row = size - len(word) * dx
#                 elif dx < 0:
#                     max_start_row = len(word) * abs(dx) - 1
#                 else:
#                     max_start_row = size - 1
                    
#                 if dy > 0:
#                     max_start_col = size - len(word) * dy
#                 elif dy < 0:
#                     max_start_col = len(word) * abs(dy) - 1
#                 else:
#                     max_start_col = size - 1
                
#                 if max_start_row < 0 or max_start_col < 0:
#                     attempts += 1
#                     continue
                
#                 start_row = random.randint(0, max_start_row)
#                 start_col = random.randint(0, max_start_col)
                
#                 # Check if word can be placed
#                 can_place = True
#                 positions = []
                
#                 for i, letter in enumerate(word):
#                     row = start_row + i * dx
#                     col = start_col + i * dy
                    
#                     if not (0 <= row < size and 0 <= col < size):
#                         can_place = False
#                         break
                        
#                     existing_letter = grid[row][col]
#                     if existing_letter != '' and existing_letter != letter:
#                         if not allow_crossing:
#                             can_place = False
#                             break
#                         # If crossing is allowed, we can overwrite only if letters match
#                         elif existing_letter != letter:
#                             can_place = False
#                             break
#                     positions.append([row, col])
                
#                 if can_place:
#                     # Place the word
#                     for i, letter in enumerate(word):
#                         row = start_row + i * dx
#                         col = start_col + i * dy
#                         grid[row][col] = letter
                    
#                     placed_words.append({
#                         'word': word,
#                         'positions': positions,
#                         'direction': [dx, dy],
#                         'start': [start_row, start_col]
#                     })
#                     placed = True
                
#                 attempts += 1
        
#         # Fill empty cells with random letters (more vowels for better word formation)
#         vowels = 'AEIOU'
#         consonant_weights = {
#             'A': 8, 'B': 2, 'C': 3, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 6,
#             'I': 7, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 7, 'O': 8, 'P': 2,
#             'Q': 1, 'R': 6, 'S': 6, 'T': 9, 'U': 3, 'V': 1, 'W': 2, 'X': 1,
#             'Y': 2, 'Z': 1
#         }
        
#         for i in range(size):
#             for j in range(size):
#                 if grid[i][j] == '':
#                     # Weighted random letter selection for more realistic grids
#                     letters = []
#                     weights = []
#                     for letter, weight in consonant_weights.items():
#                         letters.append(letter)
#                         weights.append(weight)
#                     grid[i][j] = random.choices(letters, weights=weights, k=1)[0]
        
#         self.grid = grid
#         self.words_data = placed_words
#         self.save()
        
#         return grid, placed_words
    
#     def validate_word_positions(self, positions):
#         """Validate if positions form a straight line and match a word"""
#         if len(positions) < 2:
#             return None
            
#         positions = [tuple(pos) for pos in positions]
        
#         # Check if positions form a straight line
#         rows = [pos[0] for pos in positions]
#         cols = [pos[1] for pos in positions]
        
#         # Check horizontal
#         if len(set(rows)) == 1:
#             direction = 'horizontal'
#         # Check vertical
#         elif len(set(cols)) == 1:
#             direction = 'vertical'
#         # Check diagonal
#         elif all(rows[i] - rows[0] == cols[i] - cols[0] for i in range(len(rows))):
#             direction = 'diagonal'
#         elif all(rows[i] - rows[0] == cols[0] - cols[i] for i in range(len(rows))):
#             direction = 'diagonal'
#         else:
#             return None
            
#         # Check if positions are consecutive
#         if direction in ['horizontal', 'vertical']:
#             sorted_positions = sorted(positions)
#             for i in range(1, len(sorted_positions)):
#                 if (sorted_positions[i][0] - sorted_positions[i-1][0] > 1 or 
#                     sorted_positions[i][1] - sorted_positions[i-1][1] > 1):
#                     return None
        
#         return direction

# class WordSearchGameSession(models.Model):
#     """Track user word search game sessions for progress and statistics"""
#     game = models.ForeignKey(WordSearchGame, on_delete=models.CASCADE, related_name='sessions')
#     session_id = models.CharField(max_length=100)
#     found_words = models.JSONField(default=list)
#     start_time = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(null=True, blank=True)
#     score = models.IntegerField(default=0)
#     hints_used = models.IntegerField(default=0)
#     completed = models.BooleanField(default=False)
    
#     class Meta:
#         indexes = [
#             models.Index(fields=['session_id']),
#         ]
    
#     def __str__(self):
#         return f"WordSearch Session {self.session_id} - {self.game}"

# class UserWordProgress(models.Model):
#     """Track user progress with words"""
#     user_identifier = models.CharField(max_length=100)
#     word = models.ForeignKey(WordItem, on_delete=models.CASCADE)
#     times_correct = models.IntegerField(default=0)
#     times_attempted = models.IntegerField(default=0)
#     last_played = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['user_identifier', 'word']
#         verbose_name_plural = "User word progress"
    
#     def __str__(self):
#         return f"{self.user_identifier} - {self.word.word}"
    
#     @property
#     def accuracy(self):
#         if self.times_attempted == 0:
#             return 0
#         return (self.times_correct / self.times_attempted) * 100

# # Matching Game Models
# class Category(models.Model):
#     CATEGORY_TYPES = [
#         ('animals', 'Animals'),
#         ('colors', 'Colors'),
#         ('numbers', 'Numbers'),
#         ('phonics', 'Phonics'),
#     ]
    
#     name = models.CharField(max_length=100)
#     category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
#     icon = models.CharField(max_length=10, default='📚')
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name_plural = "Categories"
    
#     def __str__(self):
#         return f"{self.name} ({self.get_category_type_display()})"
    
#     def get_random_items(self, count=4):
#         """Get random items from this category"""
#         items = list(self.items.filter(is_active=True))
#         if len(items) <= count:
#             return items
#         return random.sample(items, count)

# class LearningItem(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
#     name = models.CharField(max_length=100)
#     image = models.ImageField(upload_to='learning_items/', blank=True, null=True)
#     color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code for color category")
#     display_text = models.CharField(max_length=100, blank=True, help_text="Text to display for numbers")
#     audio = models.FileField(upload_to='audio/', blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         ordering = ['order', 'name']
    
#     def __str__(self):
#         return self.name

# class PhonicsItem(models.Model):
#     letter = models.CharField(max_length=1)
#     words = models.JSONField(default=list, help_text="List of words starting with this letter")
#     audio = models.FileField(upload_to='phonics/')
#     image = models.ImageField(upload_to='phonics/', blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         ordering = ['order', 'letter']
#         verbose_name_plural = "Phonics items"
    
#     def __str__(self):
#         return f"Phonics: {self.letter}"

# class MatchingGameSession(models.Model):
#     session_id = models.CharField(max_length=100, unique=True)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     score = models.PositiveIntegerField(default=0)
#     total_items = models.PositiveIntegerField(default=0)
#     completed = models.BooleanField(default=False)
#     time_taken = models.PositiveIntegerField(default=0, help_text="Time taken in seconds")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"Matching Session {self.session_id} - {self.category.name}"

# class UserProgress(models.Model):
#     user_identifier = models.CharField(max_length=100, help_text="Can be session ID or user ID")
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     items_completed = models.JSONField(default=list, help_text="List of completed item IDs")
#     total_score = models.PositiveIntegerField(default=0)
#     games_played = models.PositiveIntegerField(default=0)
#     levels_completed = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         verbose_name_plural = "User progress"
#         unique_together = ['user_identifier', 'category']
    
#     def __str__(self):
#         return f"Progress for {self.user_identifier} - {self.category.name}"

# class TaskSet(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='task_sets')
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     items_per_set = models.PositiveIntegerField(default=4)
#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         ordering = ['order', 'name']
    
#     def __str__(self):
#         return f"{self.category.name} - {self.name}"
    
#     def get_random_items(self):
#         """Get random items for this task set"""
#         return self.category.get_random_items(self.items_per_set)
    


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