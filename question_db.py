import json
import random

def load_geography_questions():
    try:
        with open("geography_questions.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
        return questions
    except Exception as e:
        print("Error loading geography questions:", e)
        # Fallback sample questions:
        return [
            {
                "question": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Rome"],
                "answer": 0
            },
            {
                "question": "Which country is known as the Land of the Rising Sun?",
                "options": ["China", "Japan", "South Korea", "Thailand"],
                "answer": 1
            }
        ]

def get_random_question(questions):
    return random.choice(questions)
