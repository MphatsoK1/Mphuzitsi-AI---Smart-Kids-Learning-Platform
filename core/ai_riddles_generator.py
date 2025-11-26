from groq import Groq
from django.conf import settings
import json
import random
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get API key safely
api_key = os.getenv('GROQ_API_KEY') or getattr(settings, 'GROQ_API_KEY', None)

if api_key:
    client = Groq(api_key=api_key)
else:
    logger.warning("GROQ_API_KEY not found - using fallback riddles only")
    client = None


def generate_ai_riddle(difficulty, age, topic, riddle_number=1):
    """
    Generate an AI riddle INCLUDING SMART DISTRACTORS.
    """

    if not client:
        logger.error("Groq client not initialized - using fallback riddles")
        return create_unique_fallback_riddle(1, riddle_number - 1, difficulty, topic)

    available_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]

    model = available_models[0]

    # Topic types
    question_types = {
        'easy': ['Malawian primary school riddles', 'Basic riddles', 'Funny riddles'],
        'medium': ['Advanced riddles', 'Thought-provoking riddles'],
        'hard': ['Critical thinking riddles', 'Challenging logical riddles']
    }

    q_types = question_types.get(difficulty, question_types['easy'])
    question_type = q_types[(riddle_number - 1) % len(q_types)]

    # PROMPT UPDATED — ADDS DISTRACTORS IN JSON
    prompt_templates = [
        f"""
Create a {difficulty} educational riddle about {topic} for a {age}-year-old.
Type: {question_type}.
Return 1 correct answer AND 3 plausible but wrong distractor answers.

Respond ONLY in JSON:
{{
    "question": "riddle text",
    "answer": "correct answer",
    "distractors": [
        "wrong option 1",
        "wrong option 2",
        "wrong option 3"
    ],
    "explanation": "short explanation"
}}
""",

        f"""
Generate a fun {difficulty} difficulty riddle for a {age} year old about {topic}.
Be educational, simple, and engaging. Include 3 realistic incorrect options.

Return ONLY JSON:
{{
    "question": "...",
    "answer": "...",
    "distractors": ["...", "...", "..."],
    "explanation": "..."
}}
""",

        f"""
Write a {difficulty} riddle about {topic} for a {age}-year-old.
Provide 1 correct answer and exactly 3 distractors that seem believable.

Return JSON only:
{{
    "question": "",
    "answer": "",
    "distractors": ["", "", ""],
    "explanation": ""
}}
"""
    ]

    prompt = random.choice(prompt_templates)

    try:
        logger.info(f"Generating AI riddle {riddle_number} for {age}y/o, {difficulty}, {topic}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational AI that creates riddles for kids. Always reply in VALID JSON with question, answer, distractors[], and explanation."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        logger.info(f"AI response received for riddle {riddle_number}")

        result = json.loads(result_text)

        # REQUIRED FIELDS INCLUDING DISTRACTORS
        required_keys = ['question', 'answer', 'explanation', 'distractors']

        if all(key in result for key in required_keys):
            if isinstance(result["distractors"], list) and len(result["distractors"]) == 3:
                logger.info(f"AI riddle generated successfully with distractors")
                return result

        raise ValueError("AI response missing required fields or distractors")

    except Exception as e:
        logger.error(f"AI riddle generation failed: {e}")

        difficulty_to_level = {'easy': 1, 'medium': 2, 'hard': 3}
        level_number = difficulty_to_level.get(difficulty, 1)
        index = riddle_number - 1

        fallback = create_unique_fallback_riddle(level_number, index, difficulty, topic)

        # ADD SIMPLE FALLBACK DISTRACTORS
        fallback["distractors"] = [
            "I don’t know",
            "Something else",
            "Not sure"
        ]

        return fallback


def create_unique_fallback_riddle(level_number, index, difficulty, topic):
    """
    Simple fallback riddles (no change).
    """

    fallbacks = [
        {
            'question': "I have cities, but no houses; mountains, but no trees; and water, but no fish. What am I?",
            'answer': "A map",
            'explanation': "A map shows these things but doesn't contain them physically."
        },
        {
            'question': "What has keys but can't open locks?",
            'answer': "A piano",
            'explanation': "A piano has musical keys."
        },
        {
            'question': "What gets wet while drying?",
            'answer': "A towel",
            'explanation': "A towel absorbs water while drying you."
        },
        {
            'question': "What has a head, a tail, is brown, and has no legs?",
            'answer': "A penny",
            'explanation': "A coin fits the description."
        }
    ]

    return fallbacks[index % len(fallbacks)]




# from groq import Groq
# from django.conf import settings
# import json
# import random
# import logging
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)

# # Get API key safely
# api_key = os.getenv('GROQ_API_KEY') or getattr(settings, 'GROQ_API_KEY', None)

# if api_key:
#     client = Groq(api_key=api_key)
# else:
#     logger.warning("GROQ_API_KEY not found - using fallback riddles only")
#     client = None

# def generate_ai_riddle(difficulty, age, topic, riddle_number=1):
#     """
#     Generate an AI riddle with variety based on riddle number
#     """
#     # Check if client is available
#     if not client:
#         logger.error("Groq client not initialized - using fallback riddles")
#         return create_unique_fallback_riddle(1, riddle_number - 1, difficulty, topic)

#     available_models = [
#         "llama-3.1-8b-instant",
#         "llama-3.3-70b-versatile",
#         "mixtral-8x7b-32768",
#         "gemma2-9b-it"
#     ]
    
#     model = available_models[0]
    
#     # Add variety based on riddle number and topic
#     question_types = {
#         'easy': ['Malawian primary school riddels','Basic riddles', 'funny riddles'],
#         'medium': [ 'Advanced riddles', 'thought-provoking riddles'],
#         'hard': ['Critical thinking riddles', 'puzzling riddles']
#     }
    
#     q_types = question_types.get(difficulty, question_types['easy'])
#     question_type = q_types[(riddle_number - 1) % len(q_types)]
    
#     # Different prompts for variety - UPDATED FOR RIDDLES
#     prompt_templates = [
#         f"""Create a {difficulty} level educational riddle about {topic} for a {age}-year-old.
# Question type: {question_type}
# Make it age-appropriate, engaging, funny and educational.

# Format your response as JSON:
# {{
#     "question": "riddle text here",
#     "answer": "the answer to the riddle",
#     "explanation": "brief explanation of why this is the answer"
# }}""",

#         f"""Generate a fun {difficulty} educational riddle on {topic} suitable for age {age}.
# Focus on: {question_type}
# Ensure it's age-appropriate, funny and educational.

# JSON response required:
# {{
#     "question": "riddle text",
#     "answer": "correct answer", 
#     "explanation": "why this answer makes sense"
# }}""",

#         f"""Design a {difficulty} difficulty educational riddle about {topic} for a {age} year old.
# Approach: {question_type}
# Make it age-appropriate, interesting, funny and informative.

# Respond with JSON:
# {{
#     "question": "the riddle",
#     "answer": "the solution",
#     "explanation": "educational explanation"
# }}"""
#     ]
    
#     prompt = random.choice(prompt_templates)

#     try:
#         logger.info(f"Generating AI riddle {riddle_number} for {age}y/o, {difficulty}, {topic}")
        
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {
#                     "role": "system", 
#                     "content": "You are a fun tutor who makes learning exciting by creating engaging educational riddles for children. Always respond with valid JSON. Create unique riddles each time with a clear question and answer."
#                 },
#                 {
#                     "role": "user", 
#                     "content": prompt
#                 }
#             ],
#             temperature=0.8,
#             max_tokens=500,
#             response_format={"type": "json_object"}
#         )
        
#         result_text = response.choices[0].message.content
#         logger.info(f"AI response received for riddle {riddle_number}")
        
#         result = json.loads(result_text)
        
#         # Validate the response - UPDATED FOR RIDDLES
#         required_keys = ['question', 'answer', 'explanation']
#         if all(key in result for key in required_keys):
#             logger.info(f"AI riddle {riddle_number} generated successfully")
#             return result
#         else:
#             raise ValueError("Missing required fields in AI response")
            
#     except Exception as e:
#         logger.error(f"AI riddle generation failed for riddle {riddle_number}: {e}")
        
#         # Use fallback riddle
#         difficulty_to_level = {
#             'easy': 1,
#             'medium': 2, 
#             'hard': 3
#         }
#         level_number = difficulty_to_level.get(difficulty, 1)
#         index = riddle_number - 1
        
#         return create_unique_fallback_riddle(level_number, index, difficulty, topic)


# def create_unique_fallback_riddle(level_number, index, difficulty, topic):
#     """Create unique fallback riddles"""
#     fallbacks = [
#         {
#             'question': f"I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
#             'answer': "A map",
#             'explanation': "A map shows cities, mountains, and water bodies but doesn't have actual houses, trees, or fish."
#         },
#         {
#             'question': f"What has keys but can't open locks?",
#             'answer': "A piano", 
#             'explanation': "A piano has keys that you press to make music, but they can't open physical locks."
#         },
#         {
#             'question': f"What gets wet while drying?",
#             'answer': "A towel",
#             'explanation': "A towel gets wet as it dries you or other things."
#         },
#         {
#             'question': f"What has a head, a tail, is brown, and has no legs?",
#             'answer': "A penny",
#             'explanation': "A coin has a head (front side), tail (back side), is brownish in color, and has no legs."
#         }
#     ]
    
#     fallback = fallbacks[index % len(fallbacks)]
    
#     return {
#         'question': fallback['question'],
#         'answer': fallback['answer'],
#         'explanation': fallback['explanation']
#     }