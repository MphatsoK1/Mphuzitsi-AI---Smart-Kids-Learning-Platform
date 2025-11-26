import json
import logging
import os
from dotenv import load_dotenv
from groq import Groq
from django.conf import settings

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv('GROQ_API_KEY') or getattr(settings, 'GROQ_API_KEY', None)
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None
    logger.warning("GROQ_API_KEY not configured. Math AI generation will fall back to defaults.")


def generate_ai_math_problem(difficulty, operations, min_value, max_value, age, problem_number=1):
    """
    Generate an AI math problem with JSON structure similar to quiz logic.
    """
    if not client:
        raise ValueError("Groq client not available.")

    ops = operations or ['+']
    ops_text = ", ".join(ops)

    prompt = f"""
Create a {difficulty} level math problem that only uses these operations: {ops_text}.
Use whole numbers between {min_value} and {max_value}. 
Target age: {age}. Vary between word-problems and expressions.

Return valid JSON with this structure:
{{
  "problem_text": "12 + 7",
  "display_text": "12 + 7 = ?",
  "correct_answer": 19,
  "operation": "+",
  "tip": "Add the numbers carefully.",
  "hint": "Start by adding the tens first.",
  "explanation": "12 plus 7 equals 19."
}}

Ensure correct_answer is an integer and matches the problem.
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a fun tutor who makes learning exciting by creating engaging math problems for children. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,
        max_tokens=400,
        response_format={"type": "json_object"}

        # "llama-3.1-8b-instant",
        # "llama-3.3-70b-versatile",
        # "mixtral-8x7b-32768",
        # "gemma2-9b-it"
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    required_keys = ['problem_text', 'display_text', 'correct_answer', 'operation']
    if not all(key in data for key in required_keys):
        raise ValueError("AI math problem missing required fields.")

    data['correct_answer'] = int(data['correct_answer'])
    return data

