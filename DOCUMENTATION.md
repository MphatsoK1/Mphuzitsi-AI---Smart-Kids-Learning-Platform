# Mphunzitsi-AI Documentation

## Table of Contents
1. [Views.py Documentation](#viewspy-documentation)
2. [Google Social Login Documentation](#google-social-login-documentation)
3. [Age-Based Game Filtering](#age-based-game-filtering)
4. [Authentication Flow](#authentication-flow)

---

## Views.py Documentation

### Overview
The `core/views.py` file contains all the view functions for the Mphunzitsi-AI application. These views handle authentication, game logic, user profiles, and age-based content filtering.

### File Structure
```python
# Imports and utilities
# Authentication views
# Word Capture Game views
# Word Search Game views
# Other game views
# Profile and utility views
```

---

## Authentication Views

### 1. `splash_screen(request)`

**Purpose:** Displays the splash screen (landing page) when users first visit the site.

**URL Pattern:** `''` (root URL)

**Access:** Public (unauthenticated users only)

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Behavior:**
- If user is authenticated, redirects to `home`
- If not authenticated, renders `splash_screen.html`

**Returns:** 
- `HttpResponse`: Rendered splash screen template
- `HttpResponseRedirect`: Redirect to home if authenticated

**Example:**
```python
GET /
→ Renders splash_screen.html (if not logged in)
→ Redirects to /home/ (if logged in)
```

---

### 2. `login_view(request)`

**Purpose:** Handles user login through username/email and password authentication.

**URL Pattern:** `'login/'`

**Access:** Public (redirects to home if already authenticated)

**HTTP Methods:** GET, POST

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Request Parameters (POST):**
- `username_or_email` (str): Username or email address
- `password` (str): User password

**Behavior:**
1. **GET Request:**
   - If authenticated → redirect to `home`
   - If not authenticated → render login form

2. **POST Request:**
   - Validates `LoginForm`
   - Authenticates user with `authenticate()`
   - If successful:
     - Logs in user with `login()`
     - Checks if profile is completed
     - Redirects to `profile_setup` if incomplete
     - Redirects to `home` if complete
   - If unsuccessful → shows error message

**Returns:**
- `HttpResponse`: Login form template
- `HttpResponseRedirect`: Redirect to home or profile_setup

**Example:**
```python
POST /login/
{
    "username_or_email": "john@example.com",
    "password": "secretpassword"
}
→ Authenticates user
→ Redirects to /profile-setup/ or /home/
```

**Related Files:**
- `core/forms.py` → `LoginForm`
- `core/templates/auth/login.html`

---

### 3. `register_view(request)`

**Purpose:** Handles user registration with username, email, password, and date of birth.

**URL Pattern:** `'register/'`

**Access:** Public (redirects to home if already authenticated)

**HTTP Methods:** GET, POST

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Request Parameters (POST):**
- `username` (str): Unique username
- `email` (str): Email address
- `password1` (str): Password
- `password2` (str): Password confirmation
- `date_of_birth` (date): User's date of birth (YYYY-MM-DD format)

**Behavior:**
1. **GET Request:**
   - If authenticated → redirect to `home`
   - If not authenticated → render registration form

2. **POST Request:**
   - Validates `RegisterForm`
   - Checks for duplicate username/email
   - Validates password match
   - If valid:
     - Creates user with `RegisterForm.save()`
     - Creates/updates `UserProfile` with `date_of_birth`
     - Logs in user automatically
     - Redirects to `profile_setup` for avatar selection
   - If invalid → shows error messages

**Returns:**
- `HttpResponse`: Registration form template
- `HttpResponseRedirect`: Redirect to profile_setup on success

**Example:**
```python
POST /register/
{
    "username": "johndoe",
    "email": "john@example.com",
    "password1": "SecurePass123",
    "password2": "SecurePass123",
    "date_of_birth": "2015-05-15"
}
→ Creates user account
→ Creates profile with DOB
→ Redirects to /profile-setup/
```

**Related Files:**
- `core/forms.py` → `RegisterForm`
- `core/models.py` → `User`, `UserProfile`
- `core/templates/auth/register.html`

---

### 4. `profile_setup_view(request)`

**Purpose:** Allows users to complete their profile setup by selecting an avatar and optionally providing date of birth if missing.

**URL Pattern:** `'profile-setup/'`

**Access:** Login required (`@login_required`)

**HTTP Methods:** GET, POST

**Decorators:**
- `@login_required`: Requires authentication
- `@never_cache`: Prevents browser caching (prevents back button access)

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Request Parameters (POST):**
- `selected_avatar` (str): Avatar ID (e.g., '58509039_9439767')
- `date_of_birth` (date, optional): Date of birth if not already set

**Behavior:**
1. Gets or creates `UserProfile` for the authenticated user
2. If profile is already completed → redirects to `home`
3. **GET Request:** Renders avatar selection form
4. **POST Request:**
   - Validates `ProfileSetupForm`
   - Saves selected avatar to profile
   - If `date_of_birth` is missing and provided → saves it
   - Marks profile as completed
   - Redirects to `home`

**Returns:**
- `HttpResponse`: Avatar selection template with no-cache headers
- `HttpResponseRedirect`: Redirect to home when complete

**Example:**
```python
POST /profile-setup/
{
    "selected_avatar": "58509039_9439767",
    "date_of_birth": "2015-05-15"  # Only if missing
}
→ Saves avatar selection
→ Marks profile as completed
→ Redirects to /home/
```

**Related Files:**
- `core/forms.py` → `ProfileSetupForm`
- `core/templates/choose_avatar.html`
- `core/models.py` → `UserProfile`

---

### 5. `logout_view(request)`

**Purpose:** Logs out the current user and prevents back button access to authenticated pages.

**URL Pattern:** `'logout/'`

**Access:** Public (works for both authenticated and unauthenticated users)

**HTTP Methods:** GET, POST

**Decorators:**
- `@require_http_methods(["GET", "POST"])`: Only allows GET and POST
- `@never_cache`: Prevents browser caching

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Behavior:**
1. Flushes all session data with `request.session.flush()`
2. Logs out user with Django's `logout()` function
3. Displays success message
4. Sets no-cache headers on response:
   - `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
   - `Pragma: no-cache`
   - `Expires: 0`
5. Redirects to login page

**Returns:**
- `HttpResponseRedirect`: Redirect to login page with no-cache headers

**Security Features:**
- Clears all session data
- Prevents browser from caching authenticated pages
- Prevents users from accessing cached pages via back button

**Example:**
```python
GET /logout/ or POST /logout/
→ Clears session
→ Logs out user
→ Sets no-cache headers
→ Redirects to /login/
```

**Related Files:**
- `core/middleware.py` → ProfileSetupMiddleware (also adds no-cache headers)
- `core/cache_middleware.py` → NoCacheMiddleware

---

### 6. `home_view(request)`

**Purpose:** Displays the main home page after user login.

**URL Pattern:** `'home/'`

**Access:** Login required (`@login_required`)

**HTTP Methods:** GET

**Decorators:**
- `@login_required`: Requires authentication
- `@never_cache`: Prevents browser caching

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Behavior:**
1. Checks if user profile is completed
2. If not completed → redirects to `profile_setup`
3. If completed → renders home page with no-cache headers

**Returns:**
- `HttpResponse`: Home page template with no-cache headers
- `HttpResponseRedirect`: Redirect to profile_setup if incomplete

**Cache Headers Added:**
- Prevents browser from caching the page
- Ensures fresh content on each visit

**Example:**
```python
GET /home/
→ Checks profile completion
→ Renders homepage.html (if complete)
→ Redirects to /profile-setup/ (if incomplete)
```

**Related Files:**
- `core/templates/homepage.html`
- `core/middleware.py` → ProfileSetupMiddleware

---

### 7. `profile_view(request)`

**Purpose:** Displays user profile page with statistics.

**URL Pattern:** `'profile/'`

**Access:** Login required (`@login_required`)

**HTTP Methods:** GET

**Decorators:**
- `@login_required`: Requires authentication
- `@never_cache`: Prevents browser caching

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Behavior:**
- Collects user statistics (level, points, games played, quizzes taken)
- Renders profile page

**Returns:**
- `HttpResponse`: Profile template with user stats

**Related Files:**
- `core/templates/profile.html` or `core/templates/user_profile.html`

---

## Word Capture Game Views

### 8. `capture_words(request)`

**Purpose:** Renders the Word Capture game page.

**URL Pattern:** `'capture-words/'`

**Access:** Public

**Parameters:**
- `request` (HttpRequest): The HTTP request object

**Returns:**
- `HttpResponse`: Word Capture game template

**Related Files:**
- `core/templates/capture_words.html`

---

### 9. `get_capture_words(request)`

**Purpose:** API endpoint to fetch words for Word Capture game, filtered by user age.

**URL Pattern:** `'api/capture/get-words/'`

**Access:** Public (works for both authenticated and unauthenticated users)

**HTTP Methods:** GET only (`@require_http_methods(["GET"])`)

**Query Parameters:**
- `type` (str, optional): Part of speech type (default: 'noun')
  - Options: 'noun', 'verb', 'adjective', 'adverb', 'pronoun'
- `difficulty` (str, optional): Difficulty level (default: 'easy')
  - Options: 'easy', 'medium', 'hard'
  - **Note:** This is automatically adjusted based on user age if authenticated
- `count` (int, optional): Number of words to return (default: 8)

**Behavior:**
1. Gets part of speech type from query parameters
2. If user is authenticated:
   - Retrieves user's date of birth from profile
   - Calculates user age using `get_age_from_birthdate()`
   - Determines age-appropriate difficulty using `get_difficulty_by_age()`
   - Overrides difficulty parameter with age-appropriate level
3. Filters words by:
   - Part of speech type
   - Difficulty level (age-appropriate)
   - Age filtering using `filter_by_age_appropriate()`
4. If not enough words for requested difficulty:
   - Falls back to easier difficulties (e.g., hard → medium → easy)
   - Only includes age-appropriate difficulty levels
5. Randomly selects requested number of words

**Age-Based Filtering:**
- Ages 3-6: Easy difficulty only
- Ages 7-9: Easy and Medium difficulties
- Ages 10-12: Easy, Medium, and Hard difficulties
- Ages 13+: All difficulties available

**Returns:**
- `JsonResponse` with:
  ```json
  {
    "words": ["CAT", "DOG", "SUN", ...],
    "hints": {"CAT": "A furry animal", ...},
    "type": "noun",
    "difficulty": "easy",
    "description": "A person, place, or thing",
    "hint_text": "Look for things you can see or touch"
  }
  ```

**Error Responses:**
- `404`: Part of speech not found, or not enough words available
- `500`: Server error

**Example:**
```python
GET /api/capture/get-words/?type=noun&difficulty=easy&count=8
→ Returns 8 noun words (filtered by user age if authenticated)

# For a 5-year-old user (age 3-6):
→ Automatically uses 'easy' difficulty
→ Only returns easy words

# For an 8-year-old user (age 7-9):
→ Automatically uses 'medium' difficulty
→ Can fallback to 'easy' if needed
```

**Related Files:**
- `core/models.py` → `CaptureWord`, `CapturePartOfSpeech`
- `core/game_utils.py` → Age filtering functions

---

### 10. `get_mixed_capture_words(request)`

**Purpose:** API endpoint to get a mix of different parts of speech for Word Capture game.

**URL Pattern:** `'api/capture/get-mixed-words/'`

**Access:** Public

**HTTP Methods:** GET only

**Query Parameters:**
- `difficulty` (str, optional): Difficulty level (default: 'easy')
- `target` (str, optional): Target part of speech type (default: 'noun')
- `target_count` (int, optional): Number of target words (default: 5)
- `other_count` (int, optional): Number of other words (default: 3)

**Behavior:**
- Similar to `get_capture_words()` but provides a mix of parts of speech
- Gets target words (specified type) and other words (different types)
- Filters by user age if authenticated
- Shuffles all words together

**Returns:**
- `JsonResponse` with mixed words from different parts of speech

---

### 11. `save_capture_session(request)`

**Purpose:** Saves Word Capture game session data.

**URL Pattern:** `'api/capture/save-session/'`

**Access:** Public

**HTTP Methods:** POST only (`@csrf_exempt`, `@require_http_methods(["POST"])`)

**Request Body (JSON):**
```json
{
  "player_name": "Player",
  "score": 100,
  "level": 1,
  "rounds": 5,
  "words_captured": 8,
  "time_spent": 120,
  "completed": true
}
```

**Returns:**
- `JsonResponse` with session ID and rank

---

### 12. `get_capture_leaderboard(request)`

**Purpose:** Retrieves top players for Word Capture game.

**URL Pattern:** `'api/capture/leaderboard/'`

**Access:** Public

**HTTP Methods:** GET only

**Query Parameters:**
- `limit` (int, optional): Number of top players (default: 10)

**Returns:**
- `JsonResponse` with leaderboard data

---

## Word Search Game Views

### 13. `words_search(request)`

**Purpose:** Renders the Word Search game page.

**URL Pattern:** `'words-search/'`

**Access:** Public

**Returns:**
- `HttpResponse`: Word Search game template

---

### 14. `generate_word_search_puzzle(level_number, user=None)`

**Purpose:** Helper function to generate word search puzzles, filtered by user age.

**Parameters:**
- `level_number` (int): The level number to generate
- `user` (User, optional): User object for age-based filtering

**Behavior:**
1. Filters `WordSearchLevel` by age-appropriate difficulty
2. Selects random category
3. Tries to use pre-generated puzzle from database
4. If no pre-generated puzzle, generates on-the-fly
5. Applies age-based word filtering

**Returns:**
- `dict`: Puzzle data with words, grid, positions, hints
- `None`: If level doesn't exist

---

### 15. `get_word_search_level(request)`

**Purpose:** API endpoint to get word search puzzle for a specific level.

**URL Pattern:** `'api/word-search/level/'`

**Access:** Public (filters by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int): Level number (default: 1)

**Behavior:**
- Calls `generate_word_search_puzzle()` with user context
- Filters puzzle by user age if authenticated

**Returns:**
- `JsonResponse` with puzzle data

---

### 16. `start_word_search_session(request)`

**Purpose:** Starts a new Word Search game session.

**URL Pattern:** `'api/word-search/start-session/'`

**Access:** Public

**HTTP Methods:** POST

**Request Body (JSON):**
```json
{
  "session_id": "unique-session-id",
  "player_name": "Player"
}
```

**Returns:**
- `JsonResponse` with session confirmation

---

### 17. `update_word_search_progress(request)`

**Purpose:** Updates Word Search game progress and user statistics.

**URL Pattern:** `'api/word-search/update-progress/'`

**Access:** Public (updates user progress if authenticated)

**HTTP Methods:** POST

**Behavior:**
- Updates session data
- If user is authenticated, updates `UserWordSearchProgress`
- Tracks highest level, total score, words found, perfect puzzles

---

### 18. `get_next_word_search_level(request)`

**Purpose:** Gets information about the next Word Search level.

**URL Pattern:** `'api/word-search/next-level/'`

**Access:** Public

**Query Parameters:**
- `current_level` (int): Current level number

**Returns:**
- `JsonResponse` with next level information

---

## Helper Functions

### Word Search Generation Functions

#### `generate_words_for_level(level, category, user=None)`
- Generates word lists based on level difficulty
- Filters by user age if provided
- Returns list of uppercase words

#### `generate_grid_data(words, grid_size)`
- Creates word search grid
- Places words in grid (horizontal, vertical, diagonal)
- Returns flattened grid and word positions

#### `can_place_word(grid, word, row, col, direction, grid_size)`
- Checks if word can be placed at position
- Validates grid boundaries and conflicts

#### `place_word(grid, word, row, col, direction)`
- Places word in grid
- Returns list of position indices

#### `generate_hints(words)`
- Generates simple hints for words
- Currently provides word length as hint

---

## Other Game Views

### 19. `word_search_game(request, category_id=None)`
- Renders word search game with optional category filter
- URL: `'word-search/'` or `'word-search/<int:category_id>/'`

### 20. `tracing_letters(request)`
- Renders tracing letters game
- URL: `'tracing-letters/'`

### 21. `match_game(request)`
- Renders matching game
- URL: `'match-game/'`

### 22. `artificial_intelligence(request)`
- Renders AI features page
- URL: `'artificial-intelligence/'`

### 23. `games_page(request)`
- Renders games listing page
- URL: `'games-page/'`

---

## Additional Game Modules

The following game modules are implemented in separate files and provide comprehensive age-based filtering:

---

## Math Game (`core/math_game.py`)

### Overview
The Math Game provides arithmetic problems (addition, subtraction, multiplication, division) with age-appropriate difficulty levels and number ranges.

### Views

#### `math_game(request)`
**Purpose:** Renders the Math Game page.

**URL Pattern:** `'math-game/'`

**Access:** Public

**Returns:** Math game template

---

#### `get_math_level(request)`

**Purpose:** API endpoint to get math problems for a specific level, filtered by user age.

**URL Pattern:** `'api/math-game/level/'`

**Access:** Public (filters by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int, optional): Level number (default: 1)

**Behavior:**
1. Filters `MathGameLevel` by age-appropriate difficulty using `filter_by_age_appropriate()`
2. If no age-appropriate level found, falls back to default level
3. Generates problems using `generate_math_problem()` which adjusts number ranges based on age
4. Returns JSON with level configuration and problems

**Age-Based Adjustments:**
- **Ages 3-6:** Number range limited to max 10
- **Ages 7-9:** Number range limited to max 20
- **Ages 10+:** Original number ranges from level configuration

**Returns:**
- `JsonResponse` with level data and problems
- `404`: Level not found

**Example:**
```python
GET /api/math-game/level/?level=1
→ Returns age-appropriate math problems
```

---

#### `generate_math_problem(level, user=None)`

**Purpose:** Helper function to generate a single math problem, adjusted for user age.

**Parameters:**
- `level` (int): Level number
- `user` (User, optional): User object for age filtering

**Behavior:**
1. Gets level configuration from database
2. Retrieves user age if provided
3. Adjusts `max_num` based on age:
   - Ages 3-6: Max 10
   - Ages 7-9: Max 20
   - Ages 10+: Original range
4. Generates random problem based on allowed operations (+, -, ×, ÷)
5. Returns problem text, display text, answer, and operation

**Returns:**
- `dict` with problem data

---

#### `get_next_math_level(request)`

**Purpose:** API endpoint to get next math level information, filtered by user age.

**URL Pattern:** `'api/math-game/next-level/'`

**Access:** Public (filters by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `current_level` (int): Current level number

**Behavior:**
1. Calculates next level number
2. Filters levels by age-appropriate difficulty
3. Returns next level information if available

**Returns:**
- `JsonResponse` with next level data
- `404`: No more levels

---

#### `start_math_session(request)`

**Purpose:** Starts a new Math Game session.

**URL Pattern:** `'api/math-game/start-session/'`

**HTTP Methods:** POST

**Behavior:**
- Creates `MathGameSession` with session ID
- Associates with user if authenticated

---

#### `update_math_progress(request)`

**Purpose:** Updates Math Game progress and user statistics.

**URL Pattern:** `'api/math-game/update-progress/'`

**HTTP Methods:** POST

**Behavior:**
- Updates session data (level, score, problems completed)
- Updates `UserMathProgress` if user is authenticated
- Tracks highest level, total score, perfect streaks

---

## Quiz Game (`core/quiz_game.py`)

### Overview
The Quiz Game provides multiple-choice questions across different categories and difficulty levels, all filtered by user age.

### Views

#### `quizes(request)`
**Purpose:** Renders the Quiz Game page.

**URL Pattern:** `'quizes/'`

**Returns:** Quiz game template

---

#### `get_quiz_level(request)`

**Purpose:** API endpoint to get quiz questions for a specific level, filtered by user age.

**URL Pattern:** `'api/quizes/level/'`

**Access:** Public (filters by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int, optional): Level number (default: 1)

**Behavior:**
1. Filters `QuizLevel` by age-appropriate difficulty (via `category__difficulty`)
2. Filters `QuizCategory` by age-appropriate difficulty
3. If user age available, further filters categories to match age difficulty
4. If no age-appropriate category, falls back to level's default category
5. Selects random questions from filtered categories

**Age-Based Filtering:**
- Levels filtered by category difficulty
- Categories filtered by difficulty field
- Questions selected only from age-appropriate categories

**Returns:**
- `JsonResponse` with level data and questions
- `404`: Level not found

**Example:**
```python
GET /api/quizes/level/?level=1
→ Returns age-appropriate quiz questions
```

---

#### `get_next_quiz_level(request)`

**Purpose:** API endpoint to get next quiz level information, filtered by user age.

**URL Pattern:** `'api/quizes/next-level/'`

**HTTP Methods:** GET

**Query Parameters:**
- `current_level` (int): Current level number

**Behavior:**
- Filters next level by age-appropriate difficulty
- Returns next level information if available

**Returns:**
- `JsonResponse` with next level data
- `404`: No more levels

---

#### `get_quiz_categories(request)`

**Purpose:** API endpoint to get all available quiz categories, filtered by user age.

**URL Pattern:** `'api/quizes/categories/'`

**HTTP Methods:** GET

**Behavior:**
- Filters categories by age-appropriate difficulty using `filter_by_age_appropriate()`
- Returns only categories accessible to user's age group

**Returns:**
- `JsonResponse` with filtered categories

---

#### `start_quiz_session(request)`

**Purpose:** Starts a new Quiz Game session.

**URL Pattern:** `'api/quizes/start-session/'`

**HTTP Methods:** POST

---

#### `update_quiz_progress(request)`

**Purpose:** Updates Quiz Game progress and user statistics.

**URL Pattern:** `'api/quizes/update-progress/'`

**HTTP Methods:** POST

**Behavior:**
- Updates session data
- Updates `UserQuizProgress` if authenticated
- Tracks perfect quizzes (all questions correct)

---

## Sentence Builder Game (`core/sentence_builder.py`)

### Overview
The Sentence Builder Game challenges users to arrange scrambled words into correct sentences, with age-appropriate sentence complexity.

### Views

#### `sentence_builder(request)`
**Purpose:** Renders the Sentence Builder Game page.

**URL Pattern:** `'sentence-builder/'`

**Returns:** Sentence builder template

---

#### `get_level_sentences(request)`

**Purpose:** API endpoint to get sentences for a specific level, filtered by user age.

**URL Pattern:** `'api/sentence-builder/level/'`

**Access:** Public (filters by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int, optional): Level number (default: 1)

**Behavior:**
1. Filters `SentenceBuilderLevel` by age-appropriate difficulty
2. Filters sentences by the filtered level
3. Selects random sentences up to `sentences_required`
4. Returns scrambled words and hints for each sentence

**Age-Based Filtering:**
- Levels filtered by difficulty field
- Only age-appropriate difficulty levels shown

**Returns:**
- `JsonResponse` with level data and sentences
- `404`: Level not found

---

#### `get_next_level(request)`

**Purpose:** API endpoint to get next sentence builder level information, filtered by user age.

**URL Pattern:** `'api/sentence-builder/next-level/'`

**HTTP Methods:** GET

**Behavior:**
- Filters next level by age-appropriate difficulty
- Returns next level information if available

**Returns:**
- `JsonResponse` with next level data
- `404`: No more levels

---

#### `start_sentence_session(request)`

**Purpose:** Starts a new Sentence Builder game session.

**URL Pattern:** `'api/sentence-builder/start-session/'`

**HTTP Methods:** POST

---

#### `update_sentence_progress(request)`

**Purpose:** Updates Sentence Builder game progress and user statistics.

**URL Pattern:** `'api/sentence-builder/update-progress/'`

**HTTP Methods:** POST

---

## Memory Match Game (`core/new_views.py`)

### Overview
The Memory Match Game is a card-matching game where users flip cards to find pairs. Grid size is adjusted based on user age.

### Views

#### `memory_game(request)`
**Purpose:** Renders the Memory Match Game page.

**URL Pattern:** `'memory-game/'`

**Returns:** Memory match game template

---

#### `get_level_data(request)`

**Purpose:** API endpoint to generate level data with grid size adjusted for user age.

**URL Pattern:** `'api/level/'`

**Access:** Public (adjusts complexity by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int, optional): Level number (default: 1)

**Behavior:**
1. Gets level configuration from `GameLevel` model
2. Retrieves user age if authenticated
3. **Adjusts grid size based on age:**
   - **Ages 3-6:** Maximum 2 rows × 4 columns (smaller grids)
   - **Ages 7-9:** Maximum 4 rows × 5 columns (medium grids)
   - **Ages 10+:** Original grid size (no adjustment)
4. Selects random emojis from database
5. Creates pairs and shuffles cards

**Age-Based Adjustments:**
- Grid size reduced for younger children
- Fewer pairs to match (easier)
- More manageable game complexity

**Returns:**
- `JsonResponse` with level, rows, cols, cards, and total pairs

**Example:**
```python
# For a 5-year-old user:
GET /api/level/?level=3
→ Returns smaller grid (2x4 max) instead of larger grid
```

---

#### `save_game_state(request)`

**Purpose:** Saves Memory Match game state to database.

**URL Pattern:** `'api/save-game/'`

**HTTP Methods:** POST

---

#### `load_game_state(request)`

**Purpose:** Loads Memory Match game state from database.

**URL Pattern:** `'api/load-game/'`

**HTTP Methods:** GET

---

#### `complete_level(request)`

**Purpose:** Handles level completion and updates user progress.

**URL Pattern:** `'api/complete-level/'`

**HTTP Methods:** POST

**Behavior:**
- Updates `UserGameProgress` if authenticated
- Tracks highest level and total moves
- Deactivates game session

---

## Color Splash Game (`core/color_splash_view.py`)

### Overview
The Color Splash Game challenges users to match fruits with their correct colors. Difficulty is adjusted by reducing required matches and grid size for younger children.

### Views

#### `color_splash_game(request)`
**Purpose:** Renders the Color Splash Game page.

**URL Pattern:** `'color-splash/'`

**Returns:** Color splash game template

---

#### `get_color_level_data(request)`

**Purpose:** API endpoint to generate level data with difficulty adjusted for user age.

**URL Pattern:** `'api/color-level/'`

**Access:** Public (adjusts difficulty by age if authenticated)

**HTTP Methods:** GET

**Query Parameters:**
- `level` (int, optional): Level number (default: 1)

**Behavior:**
1. Gets level configuration from `ColorSplashLevel` model
2. Retrieves user age if authenticated
3. **Adjusts difficulty based on age:**
   - **Ages 3-6:** Maximum 4 matches required, grid size max 3×3
   - **Ages 7-9:** Maximum 6 matches required, grid size max 4×4
   - **Ages 10+:** Original difficulty (no adjustment)
4. Selects random fruits from database
5. Returns fruits, colors, and adjusted level configuration

**Age-Based Adjustments:**
- Fewer matches required for younger children
- Smaller grid size for easier gameplay
- More manageable color matching

**Returns:**
- `JsonResponse` with level, required_matches, grid_size, fruits, and colors
- `400`: Not enough fruits in database

**Example:**
```python
# For a 5-year-old user:
GET /api/color-level/?level=2
→ Returns max 4 matches, grid size 3×3 (instead of harder configuration)
```

---

#### `save_color_game_state(request)`

**Purpose:** Saves Color Splash game state.

**URL Pattern:** `'api/save-color-game/'`

**HTTP Methods:** POST

---

#### `load_color_game_state(request)`

**Purpose:** Loads Color Splash game state.

**URL Pattern:** `'api/load-color-game/'`

**HTTP Methods:** GET

---

#### `complete_color_level(request)`

**Purpose:** Handles Color Splash level completion and updates user progress.

**URL Pattern:** `'api/complete-color-level/'`

**HTTP Methods:** POST

**Behavior:**
- Updates `UserColorProgress` if authenticated
- Tracks perfect matches and total score
- Deactivates game session

---

## Age-Based Filtering Implementation

### Overview
All game views and modules implement comprehensive age-based filtering to ensure age-appropriate content. The filtering uses the `game_utils.py` module and is applied across all game types.

### Age to Difficulty Mapping

| User Age | Difficulty Levels Available | Game Adjustments |
|----------|----------------------------|------------------|
| 3-6 years | Easy only | Smaller grids, fewer items, simpler content |
| 7-9 years | Easy, Medium | Medium grids, moderate complexity |
| 10-12 years | Easy, Medium, Hard | Standard grids, increased complexity |
| 13+ years | All levels (Easy, Medium, Hard, Expert) | Full access, maximum complexity |

### How It Works

1. **User Registration:**
   - User provides `date_of_birth` during registration (regular or Google signup)
   - Stored in `UserProfile.date_of_birth`

2. **Age Calculation:**
   - `get_age_from_birthdate()` calculates current age
   - Handles leap years and month/day boundaries
   - Returns `None` if date of birth is missing

3. **Difficulty Determination:**
   - `get_difficulty_by_age()` maps age to appropriate difficulty
   - Returns: 'easy', 'medium', 'hard', or None
   - Allows easier levels but restricts harder ones

4. **Query Filtering:**
   - `filter_by_age_appropriate()` filters Django querysets
   - Filters by difficulty field name (supports nested fields like `category__difficulty`)
   - Removes age-inappropriate content from results
   - Falls back to default if no age-appropriate content found

### Implementation Across Games

#### 1. **Games with Difficulty Fields**

These games use `filter_by_age_appropriate()` to filter by difficulty:

- **Word Capture** (`views.py`)
  - Filters `CaptureWord` by difficulty
  - Filters `CapturePartOfSpeech` by difficulty
  
- **Word Search** (`views.py`)
  - Filters `WordSearchLevel` by difficulty
  - Filters word generation by age

- **Math Game** (`math_game.py`)
  - Filters `MathGameLevel` by difficulty
  - Adjusts number ranges in `generate_math_problem()`
  - Ages 3-6: Max numbers 0-10
  - Ages 7-9: Max numbers 0-20
  - Ages 10+: Original ranges

- **Quiz Game** (`quiz_game.py`)
  - Filters `QuizLevel` by `category__difficulty`
  - Filters `QuizCategory` by difficulty
  - Filters questions by category difficulty

- **Sentence Builder** (`sentence_builder.py`)
  - Filters `SentenceBuilderLevel` by difficulty
  - Filters sentences by level difficulty

#### 2. **Games with Complexity Adjustment**

These games adjust complexity parameters based on age:

- **Memory Match** (`new_views.py`)
  - Adjusts grid size in `get_level_data()`
  - Ages 3-6: Max 2 rows × 4 columns
  - Ages 7-9: Max 4 rows × 5 columns
  - Ages 10+: Original grid size

- **Color Splash** (`color_splash_view.py`)
  - Adjusts `required_matches` and `grid_size` in `get_color_level_data()`
  - Ages 3-6: Max 4 matches, grid size 3×3
  - Ages 7-9: Max 6 matches, grid size 4×4
  - Ages 10+: Original difficulty

### Helper Functions (`core/game_utils.py`)

#### `get_age_from_birthdate(birthdate)`
```python
def get_age_from_birthdate(birthdate):
    """Calculate age from date of birth"""
    if not birthdate:
        return None
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age
```

**Returns:** Integer age or `None` if birthdate is missing

---

#### `get_difficulty_by_age(age)`
```python
def get_difficulty_by_age(age):
    """Map user age to game difficulty level"""
    if age is None:
        return None
    if age <= 6:
        return 'easy'      # Ages 3-6
    elif age <= 9:
        return 'medium'    # Ages 7-9
    elif age <= 12:
        return 'hard'      # Ages 10-12
    else:
        return 'hard'      # Ages 13+ (allows all in filtering)
```

**Returns:** 'easy', 'medium', 'hard', or `None`

---

#### `filter_by_age_appropriate(user, queryset, difficulty_field='difficulty')`
```python
def filter_by_age_appropriate(user, queryset, difficulty_field='difficulty'):
    """Filter a queryset by user's age-appropriate difficulty level"""
    # Gets user age
    # Determines appropriate difficulty
    # Filters queryset to include only allowed difficulties
    # Returns filtered queryset
```

**Parameters:**
- `user`: User instance (can be None)
- `queryset`: Django queryset to filter
- `difficulty_field`: Field name for difficulty (supports nested like `category__difficulty`)

**Returns:** Filtered queryset with only age-appropriate difficulties

**Behavior:**
- If no user/profile: Returns all non-null difficulties
- If no age: Returns all non-null difficulties
- If age available: Filters to include easier levels up to age-appropriate level
  - Age 3-6: Only 'easy'
  - Age 7-9: 'easy' and 'medium'
  - Age 10-12: 'easy', 'medium', 'hard'
  - Age 13+: All difficulties

---

#### `get_age_range_for_difficulty(difficulty)`
```python
def get_age_range_for_difficulty(difficulty):
    """Get age range for a given difficulty level"""
    difficulty_map = {
        'easy': (3, 6),
        'medium': (7, 9),
        'hard': (10, 12),
        'expert': (13, 100),
    }
    return difficulty_map.get(difficulty, None)
```

**Returns:** Tuple of (min_age, max_age) or `None`

---

### Example Flow

#### Example 1: Word Capture (Difficulty-Based Filtering)

```python
# User: 5 years old, DOB: 2019-05-15
User registers → DOB saved to UserProfile

# Frontend requests words:
GET /api/capture/get-words/?type=noun&difficulty=easy&count=8

# Backend processing:
1. get_capture_words(request) called
2. User authenticated → user.profile.date_of_birth retrieved
3. get_age_from_birthdate() → age = 5
4. get_difficulty_by_age(5) → 'easy'
5. filter_by_age_appropriate(user, queryset, 'difficulty')
   → Filters CaptureWord to only 'easy' difficulty
6. Returns: 8 easy nouns suitable for age 5
```

#### Example 2: Memory Match (Complexity Adjustment)

```python
# User: 5 years old
GET /api/level/?level=3

# Backend processing:
1. get_level_data(request) called
2. User age = 5
3. Level 3 would normally be 3 rows × 4 columns
4. Age check: user_age <= 6 → Apply age adjustment
5. rows = min(3, 2) = 2
6. cols = min(4, 4) = 4
7. Returns: 2 rows × 4 columns (8 cards, 4 pairs)
   → Easier for 5-year-old than original 3×4 grid
```

#### Example 3: Math Game (Dual Filtering)

```python
# User: 8 years old
GET /api/math-game/level/?level=1

# Backend processing:
1. get_math_level(request) called
2. Filter MathGameLevel by difficulty → 'medium' (age 8)
3. generate_math_problem(level=1, user=user)
4. Age check: user_age <= 9 → Max number = 20
5. Generates problems like: 12 + 7 = ?, 18 - 5 = ?
   → Number range limited to 0-20 instead of higher
```

---

### Benefits of Age-Based Filtering

1. **Safety:** Ensures content is appropriate for child's age
2. **Engagement:** Prevents frustration from overly difficult content
3. **Progression:** Allows gradual skill building
4. **Compliance:** Helps meet age-appropriate content requirements
5. **User Experience:** Tailored experience for each age group

---

### Testing Age Filtering

**Test Scenarios:**

1. **Create test users with different ages:**
   ```python
   # Age 5 user
   user5 = User.objects.create_user(username='child5', ...)
   user5.profile.date_of_birth = date(2019, 1, 1)
   
   # Age 8 user
   user8 = User.objects.create_user(username='child8', ...)
   user8.profile.date_of_birth = date(2016, 1, 1)
   
   # Age 12 user
   user12 = User.objects.create_user(username='child12', ...)
   user12.profile.date_of_birth = date(2012, 1, 1)
   ```

2. **Test API endpoints with different users:**
   - Verify age 5 only gets 'easy' content
   - Verify age 8 gets 'easy' and 'medium' content
   - Verify age 12 gets 'easy', 'medium', and 'hard' content

3. **Test complexity adjustments:**
   - Memory Match: Verify grid sizes adjusted
   - Color Splash: Verify matches and grid size adjusted
   - Math Game: Verify number ranges adjusted

4. **Test fallback behavior:**
   - Verify unauthenticated users get default content
   - Verify missing DOB returns all content
   - Verify missing levels fall back to defaults

---

## Google Social Login Documentation

### Overview
The application uses Django Allauth for Google OAuth authentication. The implementation includes custom forms and adapters to collect date of birth during social signup.

---

## Architecture Overview

### Components

1. **Django Allauth**
   - Handles OAuth flow with Google
   - Manages social account connections
   - URL: `'accounts/'` prefix

2. **Custom Adapters** (`core/adapters.py`)
   - `CustomSocialAccountAdapter`: Handles social logins
   - `CustomAccountAdapter`: Handles regular signups

3. **Custom Forms** (`core/allauth_forms.py`)
   - `CustomSignupForm`: Regular allauth signup with DOB
   - `CustomSocialSignupForm`: Social signup with DOB

4. **Custom Templates**
   - `core/templates/account/login.html`: Allauth login
   - `core/templates/account/signup.html`: Allauth signup
   - `core/templates/socialaccount/login.html`: Google login confirmation
   - `core/templates/socialaccount/signup.html`: Google signup form

---

## Google Login Flow

### Step-by-Step Process

#### 1. **Initial Login Request**

**User Action:** Clicks "Sign in with Google" or "Sign up with Google"

**Template Code:**
```django
<a href="{% provider_login_url 'google' %}?next={% url 'home' %}">
    Sign in with Google
</a>
```

**What Happens:**
- Generates Google OAuth URL using `provider_login_url` template tag
- Includes `next` parameter for redirect after authentication
- User is redirected to Google's authentication page

**URL Generated:**
```
/accounts/google/login/?process=login&next=/home/
```

---

#### 2. **Google Authentication**

**User Action:** Authenticates with Google account

**What Happens:**
- User redirected to Google OAuth consent screen
- User grants permissions (email, profile)
- Google redirects back to callback URL:
  ```
  /accounts/google/login/callback/
  ```

---

#### 3. **Callback Processing**

**Django Allauth Processing:**
- Receives OAuth authorization code from Google
- Exchanges code for access token
- Retrieves user information from Google API
- Checks if social account exists in database

**Two Scenarios:**

**A. New User (No Social Account):**
- Since `SOCIALACCOUNT_AUTO_SIGNUP = False` in settings
- User is redirected to signup form (`/accounts/social/signup/`)
- Custom template `socialaccount/signup.html` is rendered

**B. Existing User (Social Account Exists):**
- User is logged in automatically
- Redirected to `next` URL (usually `/home/`)

---

#### 4. **Social Signup Form (New Users Only)**

**URL:** `/accounts/social/signup/`

**Template:** `core/templates/socialaccount/signup.html`

**Form:** `CustomSocialSignupForm` from `core/allauth_forms.py`

**Fields Required:**
- `username`: Auto-filled or user must choose
- `email`: Pre-filled from Google (if available)
- `date_of_birth`: **Required field** - User must provide

**What Happens:**
1. Form displays with Google account info pre-filled
2. User must provide:
   - Username (if not auto-generated)
   - Date of birth (required for age filtering)
3. Form submission triggers `CustomSocialSignupForm.save()`

---

#### 5. **Account Creation**

**When Form is Submitted:**

1. **Form Validation:**
   ```python
   # core/allauth_forms.py
   def clean_date_of_birth(self):
       # Validates age is between 3-100 years
       # Returns date_of_birth or raises ValidationError
   ```

2. **User Creation:**
   ```python
   # CustomSocialSignupForm.save()
   user = super().save(request)  # Creates User account
   ```

3. **Profile Creation:**
   ```python
   # Gets or creates UserProfile
   profile = UserProfile.objects.get_or_create(user=user)
   profile.date_of_birth = form.cleaned_data['date_of_birth']
   profile.save()
   ```

4. **Social Account Linking:**
   - Allauth creates `SocialAccount` linking Google to User
   - User is automatically logged in

---

#### 6. **Post-Signup Redirect**

**After Successful Signup:**
- User is redirected to `next` URL (from step 1)
- If no `next`, uses `LOGIN_REDIRECT_URL = 'home'`
- User may be redirected to `profile_setup` if avatar not selected

---

## Configuration Files

### 1. Settings (`aphunzitsi_ai/settings.py`)

```python
# Allauth Configuration
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 2  # Required for allauth

# Google OAuth Provider Settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"}
    }
}

# Custom Adapters
ACCOUNT_ADAPTER = 'core.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'core.adapters.CustomSocialAccountAdapter'

# Custom Forms
ACCOUNT_FORMS = {
    'signup': 'core.allauth_forms.CustomSignupForm',
}
SOCIALACCOUNT_FORMS = {
    'signup': 'core.allauth_forms.CustomSocialSignupForm',
}

# Disable Auto Signup (to collect date_of_birth)
SOCIALACCOUNT_AUTO_SIGNUP = False

# Authentication Backends
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
)
```

---

### 2. URL Configuration

**Main URLs** (`aphunzitsi_ai/urls.py`):
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),  # Allauth URLs
    path('', include('core.urls')),
]
```

**Allauth URLs Include:**
- `/accounts/login/` - Allauth login page
- `/accounts/signup/` - Allauth signup page
- `/accounts/google/login/` - Start Google OAuth
- `/accounts/google/login/callback/` - Google OAuth callback
- `/accounts/social/signup/` - Social signup form
- `/accounts/logout/` - Allauth logout

---

### 3. Custom Adapter (`core/adapters.py`)

#### `CustomSocialAccountAdapter`

**Purpose:** Customizes social account (Google) signup process

**Key Methods:**

1. **`is_open_for_signup(request, socialaccount)`**
   - Returns `True` to allow social signups
   - Could add logic to restrict signups if needed

2. **`save_user(request, sociallogin, form=None)`**
   - Called after form submission
   - Saves user account
   - If `date_of_birth` in form → saves to `UserProfile`

3. **`populate_user(request, sociallogin, data)`**
   - Populates user data from Google account
   - Pre-fills email, username from Google profile

---

#### `CustomAccountAdapter`

**Purpose:** Customizes regular (non-social) account signup

**Key Methods:**

1. **`save_user(request, user, form, commit=True)`**
   - Saves user from regular signup form
   - Extracts `date_of_birth` from form
   - Saves to `UserProfile`

---

### 4. Custom Forms (`core/allauth_forms.py`)

#### `CustomSignupForm`

**Base Class:** `allauth.account.forms.SignupForm`

**Additional Fields:**
- `date_of_birth` (DateField, required)

**Validation:**
- Age must be between 3-100 years
- Raises `ValidationError` if invalid

**Save Method:**
- Creates user account
- Creates/updates `UserProfile` with `date_of_birth`

---

#### `CustomSocialSignupForm`

**Base Class:** `allauth.socialaccount.forms.SignupForm`

**Additional Fields:**
- `date_of_birth` (DateField, required)

**Same Validation and Save Logic as `CustomSignupForm`**

**Differences:**
- Used specifically for social account signups
- Google account info (email) may be pre-filled

---

## Templates

### 1. `core/templates/account/login.html`

**Purpose:** Allauth login page (alternative to custom login)

**Features:**
- Styled to match app design
- Includes Google login button
- Links to signup page

**Google Login Button:**
```django
{% for provider in socialaccount_providers %}
    <a href="{% provider_login_url provider.id process='login' %}">
        Sign in with {{ provider.name }}
    </a>
{% endfor %}
```

---

### 2. `core/templates/account/signup.html`

**Purpose:** Allauth signup page with date_of_birth field

**Features:**
- Styled form matching app design
- Includes `date_of_birth` field
- Google signup option

---

### 3. `core/templates/socialaccount/login.html`

**Purpose:** Confirmation page before Google authentication

**Shows:**
- "You are about to sign in using a third-party account from Google"
- Continue button
- Menu links

**URL:** `/accounts/google/login/`

---

### 4. `core/templates/socialaccount/signup.html`

**Purpose:** Signup form shown after Google authentication (new users)

**Shows:**
- Pre-filled information from Google
- Username field (required)
- Email field (optional, pre-filled)
- **Date of Birth field (required)**

**URL:** `/accounts/social/signup/`

**Important:** This is where new Google users must provide their date of birth before account creation.

---

## Complete Google Login Flow Diagram

```
User clicks "Sign in with Google"
         ↓
/accounts/google/login/
         ↓
[Google OAuth Consent Screen]
         ↓
User authenticates with Google
         ↓
/accounts/google/login/callback/
         ↓
    ┌─────────────┐
    │ Account     │
    │ Exists?     │
    └─────────────┘
         │
    ┌────┴────┐
   Yes       No
    │         │
    │         ↓
    │  /accounts/social/signup/
    │         │
    │  [Show CustomSocialSignupForm]
    │         │
    │  [User provides DOB]
    │         │
    │         ↓
    │  CustomSocialAccountAdapter.save_user()
    │         │
    │  [Create User + Profile with DOB]
    │         │
    ↓         ↓
[User Logged In]
         ↓
Redirect to /home/ (or next URL)
         ↓
ProfileSetupMiddleware checks profile
         ↓
If incomplete → /profile-setup/
If complete → /home/
```

---

## Security Features

### 1. **CSRF Protection**
- All forms include CSRF tokens
- Django's CSRF middleware enabled

### 2. **Session Security**
- Sessions stored in database
- Session cookie age: 1 hour
- Sessions saved on each request

### 3. **Cache Prevention**
- `@never_cache` decorator on authenticated views
- No-cache headers prevent browser caching
- Prevents back button access after logout

### 4. **Authentication Backends**
- Django's ModelBackend (username/password)
- Allauth's AuthenticationBackend (social accounts)

---

## URL Patterns Summary

### Authentication URLs

| URL Pattern | View Function | Purpose |
|------------|---------------|---------|
| `/` | `splash_screen` | Landing page |
| `/login/` | `login_view` | Custom login page |
| `/register/` | `register_view` | Custom registration |
| `/logout/` | `logout_view` | Logout |
| `/profile-setup/` | `profile_setup_view` | Avatar selection |
| `/home/` | `home_view` | Home page |

### Allauth URLs (Auto-generated)

| URL Pattern | Purpose |
|------------|---------|
| `/accounts/login/` | Allauth login page |
| `/accounts/signup/` | Allauth signup page |
| `/accounts/google/login/` | Start Google OAuth |
| `/accounts/google/login/callback/` | Google OAuth callback |
| `/accounts/social/signup/` | Social signup form (DOB required) |
| `/accounts/logout/` | Allauth logout |

### Game API URLs

| URL Pattern | View Function | Purpose |
|------------|---------------|---------|
| `/api/capture/get-words/` | `get_capture_words` | Get Word Capture words |
| `/api/capture/get-mixed-words/` | `get_mixed_capture_words` | Get mixed words |
| `/api/capture/save-session/` | `save_capture_session` | Save game session |
| `/api/capture/leaderboard/` | `get_capture_leaderboard` | Get leaderboard |
| `/api/word-search/level/` | `get_word_search_level` | Get Word Search puzzle |
| `/api/word-search/start-session/` | `start_word_search_session` | Start session |
| `/api/word-search/update-progress/` | `update_word_search_progress` | Update progress |
| `/api/word-search/next-level/` | `get_next_word_search_level` | Next level info |

---

## Error Handling

### Common Errors

1. **400 Bad Request**
   - Invalid form data
   - Missing required fields

2. **404 Not Found**
   - Level doesn't exist
   - Part of speech not found
   - Not enough words available

3. **500 Internal Server Error**
   - Server-side exceptions
   - Database errors

### Error Responses Format

```json
{
  "error": "Error message here",
  "status": "error"
}
```

---

## Best Practices Implemented

1. **Age-Based Filtering**
   - All game content filtered by user age
   - Ensures age-appropriate content

2. **Cache Prevention**
   - Prevents unauthorized access via browser cache
   - No-cache headers on authenticated pages

3. **Session Management**
   - Proper session clearing on logout
   - Session data validation

4. **Form Validation**
   - Client-side and server-side validation
   - Custom validation for date of birth

5. **Error Handling**
   - Try-except blocks in API views
   - Meaningful error messages
   - Proper HTTP status codes

---

## Testing Recommendations

### Authentication Flow Testing

1. **Regular Registration:**
   - Register with valid data
   - Verify date_of_birth is saved
   - Check profile creation

2. **Google Login (New User):**
   - Click "Sign up with Google"
   - Authenticate with Google
   - Complete signup form with DOB
   - Verify account creation

3. **Google Login (Existing User):**
   - Click "Sign in with Google"
   - Authenticate with Google
   - Verify automatic login
   - Check redirect to home

4. **Logout:**
   - Logout user
   - Try accessing protected pages
   - Verify back button doesn't work
   - Check session is cleared

### Age Filtering Testing

1. **Test Age Groups:**
   - Register users with different ages
   - Verify appropriate difficulty levels
   - Check content is filtered correctly

2. **Test Game APIs:**
   - Request words with different user ages
   - Verify age-appropriate content returned
   - Check fallback to easier levels

---

## Additional Resources

### Django Allauth Documentation
- https://django-allauth.readthedocs.io/

### Google OAuth Documentation
- https://developers.google.com/identity/protocols/oauth2

### Django Documentation
- https://docs.djangoproject.com/

---

## Summary

This documentation covers:

1. **All views in `views.py`** with detailed explanations
2. **Google Social Login** implementation and flow
3. **Age-based filtering** system
4. **Authentication and authorization** mechanisms
5. **Security features** including cache prevention
6. **URL patterns** and routing
7. **Error handling** strategies

The application uses Django Allauth for social authentication, custom adapters and forms to collect date of birth, and comprehensive age-based filtering to ensure age-appropriate content for all users.

