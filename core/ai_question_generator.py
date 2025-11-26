from groq import Groq
from django.conf import settings
import json
import random
import logging

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_ai_question(difficulty, age, topic, question_number=1):
    """
    Generate an AI question with variety based on question number
    """
    available_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    model = available_models[0]  # Use the first available model
    #model = random.choice(available_models)
    
    # Add variety based on question number and topic
    question_types = {
        'easy': ['Presidents of Africa','basic fact', 'identification', 'matching','multiple choice', 'fill-in-blank'],
        'medium': ['African natural resources','application', 'comparison', 'explanation', 'analysis', 'short answer', 'sequence'],
        'hard': ['Malawian History','Mining in Africa','critical thinking', 'problem solving', 'evaluation', 'synthesis']
    }
    
    q_types = question_types.get(difficulty, question_types['easy'])
    question_type = q_types[(question_number - 1) % len(q_types)]
    
    # Different prompts for variety
    prompt_templates = [
        f"""Create a {difficulty} level quiz question about {topic} for a {age}-year-old.
Question type: {question_type}
Make it engaging and educational.

Format your response as JSON:
{{
    "question": "question here",
    "options": ["A", "B", "C", "D"],
    "correct": "A",
    "explanation": "brief explanation"
}}""",

        f"""Generate a fun {difficulty} quiz question on {topic} suitable for age {age}.
Focus on: {question_type}
Ensure it's age-appropriate and educational.

JSON response required:
{{
    "question": "question text",
    "options": ["option 1", "option 2", "option 3", "option 4"],
    "correct": "correct letter",
    "explanation": "why it's correct"
}}""",

        f"""Design a {difficulty} difficulty question about {topic} for a {age} year old.
Approach: {question_type}
Make it interesting and informative.

Respond with JSON:
{{
    "question": "the question",
    "options": ["A", "B", "C", "D"],
    "correct": "A",
    "explanation": "educational explanation"
}}"""
    ]
    
    prompt = random.choice(prompt_templates)

    try:
        logger.info(f"Generating AI question {question_number} for {age}y/o, {difficulty}, {topic}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a fun tutor who makes learning exciting by creating engaging quiz questions for children. Always respond with valid JSON. Create unique questions each time."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.8,  # Higher temperature for more variety
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        logger.info(f"AI response received for question {question_number}")
        
        result = json.loads(result_text)
        
        # Validate the response
        required_keys = ['question', 'options', 'correct', 'explanation']
        if all(key in result for key in required_keys):
            if len(result['options']) == 4 and result['correct'] in ['A', 'B', 'C', 'D']:
                logger.info(f"AI question {question_number} generated successfully")
                return result
            else:
                raise ValueError("Invalid options or correct answer format")
        else:
            raise ValueError("Missing required fields in AI response")
            
    except Exception as e:
        logger.error(f"AI question generation failed for question {question_number}: {e}")
        
        # Map difficulty to level number
        difficulty_to_level = {
            'easy': 1,
            'medium': 2, 
            'hard': 3
        }
        level_number = difficulty_to_level.get(difficulty, 1)
        index = question_number - 1
        
        fallback_result = create_unique_fallback_question(level_number, index, difficulty, topic)
        
        # Convert the fallback format to match AI response format
        return {
            'question': fallback_result['question_text'],
            'options': [opt['text'] for opt in fallback_result['options']],
            'correct': fallback_result['correct_option'],
            'explanation': fallback_result['explanation']
        }


def create_unique_fallback_question(level_number, index, difficulty, topic):
    """Create unique fallback questions"""
    fallbacks = [
        {
            'question': f"Level {level_number}: What is {index + 1} + {level_number}?",
            'options': [str(index + 1), str(index + 2), str(index + 1 + level_number), str(index + level_number + 2)],
            'correct': "C",
            'explanation': f"{index + 1} + {level_number} = {index + 1 + level_number}"
        },
        {
            'question': f"Level {level_number}: Which number is largest?",
            'options': [str(level_number), str(index + 1), str(level_number + index + 5), str(level_number * 2)],
            'correct': "C",
            'explanation': f"{level_number + index + 5} is the largest number."
        }
    ]
    
    return {
        'id': f"fallback_{level_number}_{index}",
        'question_text': fallbacks[index % len(fallbacks)]['question'],
        'options': [
            {'letter': 'A', 'text': fallbacks[index % len(fallbacks)]['options'][0]},
            {'letter': 'B', 'text': fallbacks[index % len(fallbacks)]['options'][1]},
            {'letter': 'C', 'text': fallbacks[index % len(fallbacks)]['options'][2]},
            {'letter': 'D', 'text': fallbacks[index % len(fallbacks)]['options'][3]}
        ],
        'correct_option': fallbacks[index % len(fallbacks)]['correct'],
        'explanation': fallbacks[index % len(fallbacks)]['explanation'],
        'points': 10,
        'is_ai': False
    }
