# populate_capture_words_script.py
import os
import django

# ✅ Set up Django environment (update this path if necessary)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aphunzitsi_ai.settings')
django.setup()

from core.models import CapturePartOfSpeech, CaptureWord

def populate_capture_words():
    # === Define Parts of Speech ===
    pos_data = [
        ('noun', 'Naming words - people, places, things', 'Words that name things!'),
        ('verb', 'Action words - what you can do', 'Words that show action!'),
        ('adjective', 'Describing words - how things look or feel', 'Words that describe!'),
        ('adverb', 'Words that tell how, when, or where actions happen', 'They describe actions!'),
        ('pronoun', 'Words used instead of nouns', 'Words like he, she, it!'),
    ]

    # === Create or get parts of speech ===
    for name, desc, hint in pos_data:
        CapturePartOfSpeech.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'hint_text': hint}
        )

    # === Define words for each part of speech ===
    words_data = [
        # --- Nouns ---
        ('DOG', 'noun', 'easy', 'A pet that barks'),
        ('CAT', 'noun', 'easy', 'A pet that meows'),
        ('BALL', 'noun', 'easy', 'Round toy you throw'),
        ('BOOK', 'noun', 'easy', 'You read this'),
        ('TREE', 'noun', 'easy', 'Tall plant with leaves'),
        ('HOUSE', 'noun', 'easy', 'Where you live'),
        ('CAR', 'noun', 'easy', 'Drives on roads'),
        ('SUN', 'noun', 'easy', 'Shines in the sky'),
        ('BIRD', 'noun', 'easy', 'Flies in the sky'),
        ('CHAIR', 'noun', 'easy', 'You sit on it'),

        ('MOUNTAIN', 'noun', 'medium', 'Very tall landform'),
        ('RIVER', 'noun', 'medium', 'Flows with water'),
        ('FOREST', 'noun', 'medium', 'Has many trees'),
        ('CITY', 'noun', 'medium', 'Large town'),
        ('TEACHER', 'noun', 'medium', 'Helps you learn'),
        ('STUDENT', 'noun', 'medium', 'Learns in school'),
        ('PLANET', 'noun', 'medium', 'Orbits the sun'),
        ('COMPUTER', 'noun', 'medium', 'Used for typing and games'),
        ('OCEAN', 'noun', 'medium', 'A huge body of water'),
        ('BRIDGE', 'noun', 'medium', 'Connects two places'),

        ('INVENTION', 'noun', 'hard', 'Something newly created'),
        ('UNIVERSE', 'noun', 'hard', 'Everything in space'),
        ('HAPPINESS', 'noun', 'hard', 'Feeling of great joy'),
        ('FRIENDSHIP', 'noun', 'hard', 'Bond between friends'),
        ('DISCOVERY', 'noun', 'hard', 'Finding something new'),
        ('COURAGE', 'noun', 'hard', 'Bravery in difficult times'),
        ('EXPERIMENT', 'noun', 'hard', 'Scientific test'),
        ('LANGUAGE', 'noun', 'hard', 'How we communicate'),
        ('EVIDENCE', 'noun', 'hard', 'Proof of something'),
        ('KNOWLEDGE', 'noun', 'hard', 'What you know'),

        # --- Verbs ---
        ('RUN', 'verb', 'easy', 'Move fast with legs'),
        ('JUMP', 'verb', 'easy', 'Go up in the air'),
        ('EAT', 'verb', 'easy', 'Put food in mouth'),
        ('PLAY', 'verb', 'easy', 'Have fun'),
        ('SING', 'verb', 'easy', 'Make music with your voice'),
        ('DANCE', 'verb', 'easy', 'Move to music'),
        ('SLEEP', 'verb', 'easy', 'Rest at night'),
        ('READ', 'verb', 'easy', 'Look at words in books'),
        ('DRAW', 'verb', 'easy', 'Make pictures'),
        ('WRITE', 'verb', 'easy', 'Use a pen or pencil'),

        ('CLIMB', 'verb', 'medium', 'Go up using hands and feet'),
        ('SHOUT', 'verb', 'medium', 'Speak very loudly'),
        ('LISTEN', 'verb', 'medium', 'Hear carefully'),
        ('BUILD', 'verb', 'medium', 'Make something'),
        ('DRIVE', 'verb', 'medium', 'Operate a car'),
        ('COOK', 'verb', 'medium', 'Make food'),
        ('PAINT', 'verb', 'medium', 'Color something'),
        ('STUDY', 'verb', 'medium', 'Learn carefully'),
        ('CLEAN', 'verb', 'medium', 'Make something tidy'),
        ('TEACH', 'verb', 'medium', 'Help others learn'),

        ('INVESTIGATE', 'verb', 'hard', 'Look for answers'),
        ('DISCOVER', 'verb', 'hard', 'Find something new'),
        ('ANALYZE', 'verb', 'hard', 'Study closely'),
        ('EXPLAIN', 'verb', 'hard', 'Make someone understand'),
        ('DECIDE', 'verb', 'hard', 'Choose something'),
        ('DESCRIBE', 'verb', 'hard', 'Say what it’s like'),
        ('COMPARE', 'verb', 'hard', 'Find similarities or differences'),
        ('OBSERVE', 'verb', 'hard', 'Watch carefully'),
        ('IMAGINE', 'verb', 'hard', 'Think creatively'),
        ('CREATE', 'verb', 'hard', 'Make something new'),

        # --- Adjectives ---
        ('BIG', 'adjective', 'easy', 'Very large'),
        ('SMALL', 'adjective', 'easy', 'Tiny, not big'),
        ('HAPPY', 'adjective', 'easy', 'Feeling good'),
        ('SAD', 'adjective', 'easy', 'Feeling bad'),
        ('HOT', 'adjective', 'easy', 'Very warm'),
        ('COLD', 'adjective', 'easy', 'Not warm'),
        ('FAST', 'adjective', 'easy', 'Very quick'),
        ('SLOW', 'adjective', 'easy', 'Not fast'),
        ('CLEAN', 'adjective', 'easy', 'Not dirty'),
        ('DIRTY', 'adjective', 'easy', 'Needs cleaning'),

        ('BRAVE', 'adjective', 'medium', 'Not afraid'),
        ('KIND', 'adjective', 'medium', 'Nice to others'),
        ('LOUD', 'adjective', 'medium', 'Not quiet'),
        ('QUIET', 'adjective', 'medium', 'Not loud'),
        ('SHINY', 'adjective', 'medium', 'Reflects light'),
        ('SOFT', 'adjective', 'medium', 'Gentle to touch'),
        ('STRONG', 'adjective', 'medium', 'Full of power'),
        ('WEAK', 'adjective', 'medium', 'Not strong'),
        ('FUNNY', 'adjective', 'medium', 'Makes you laugh'),
        ('BRIGHT', 'adjective', 'medium', 'Full of light'),

        ('GENEROUS', 'adjective', 'hard', 'Gives to others'),
        ('CURIOUS', 'adjective', 'hard', 'Wants to know more'),
        ('TALENTED', 'adjective', 'hard', 'Has special skill'),
        ('HONEST', 'adjective', 'hard', 'Tells the truth'),
        ('CREATIVE', 'adjective', 'hard', 'Full of new ideas'),
        ('POLITE', 'adjective', 'hard', 'Has good manners'),
        ('HELPFUL', 'adjective', 'hard', 'Gives support'),
        ('CONFIDENT', 'adjective', 'hard', 'Sure of yourself'),
        ('AMAZING', 'adjective', 'hard', 'Very impressive'),
        ('BRILLIANT', 'adjective', 'hard', 'Very smart or bright'),

        # --- Adverbs ---
        ('QUICKLY', 'adverb', 'easy', 'In a fast way'),
        ('SLOWLY', 'adverb', 'easy', 'Not fast'),
        ('LOUDLY', 'adverb', 'easy', 'With a lot of sound'),
        ('SOFTLY', 'adverb', 'easy', 'In a gentle way'),
        ('HAPPILY', 'adverb', 'easy', 'With joy'),
        ('SADLY', 'adverb', 'easy', 'With sadness'),
        ('CAREFULLY', 'adverb', 'medium', 'With care'),
        ('ANGRILY', 'adverb', 'medium', 'In an angry way'),
        ('BRAVELY', 'adverb', 'medium', 'With courage'),
        ('SILENTLY', 'adverb', 'medium', 'Without noise'),
        ('EASILY', 'adverb', 'medium', 'Without effort'),
        ('HONESTLY', 'adverb', 'hard', 'In a truthful way'),
        ('PROUDLY', 'adverb', 'hard', 'With pride'),
        ('GRACEFULLY', 'adverb', 'hard', 'In an elegant way'),
        ('CAUTIOUSLY', 'adverb', 'hard', 'With caution'),
        ('PATIENTLY', 'adverb', 'hard', 'Without hurry'),

        # --- Pronouns ---
        ('HE', 'pronoun', 'easy', 'Boy or man'),
        ('SHE', 'pronoun', 'easy', 'Girl or woman'),
        ('IT', 'pronoun', 'easy', 'For a thing or animal'),
        ('THEY', 'pronoun', 'easy', 'More than one person'),
        ('WE', 'pronoun', 'easy', 'You and me'),
        ('YOU', 'pronoun', 'easy', 'The person being spoken to'),
        ('I', 'pronoun', 'easy', 'The speaker'),
        ('ME', 'pronoun', 'easy', 'Used for yourself'),
        ('US', 'pronoun', 'easy', 'Includes you and me'),
        ('THEM', 'pronoun', 'easy', 'Refers to other people'),
    ]

    # === Populate words ===
    for word, pos_name, difficulty, hint in words_data:
        pos = CapturePartOfSpeech.objects.get(name=pos_name)
        CaptureWord.objects.get_or_create(
            word=word,
            part_of_speech=pos,
            difficulty=difficulty,
            defaults={'hint': hint}
        )

    print("✅ Successfully populated Capture Parts of Speech and Words!")

if __name__ == "__main__":
    populate_capture_words()
