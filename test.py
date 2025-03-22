import json
import random

# List of 50 country-capital pairs.
country_capitals = [
    ("France", "Paris"),
    ("United Kingdom", "London"),
    ("Japan", "Tokyo"),
    ("Canada", "Ottawa"),
    ("Egypt", "Cairo"),
    ("Germany", "Berlin"),
    ("Brazil", "Brasília"),
    ("Russia", "Moscow"),
    ("Australia", "Canberra"),
    ("India", "New Delhi"),
    ("Italy", "Rome"),
    ("Spain", "Madrid"),
    ("Mexico", "Mexico City"),
    ("South Korea", "Seoul"),
    ("Netherlands", "Amsterdam"),
    ("Sweden", "Stockholm"),
    ("Norway", "Oslo"),
    ("Switzerland", "Bern"),
    ("Belgium", "Brussels"),
    ("Austria", "Vienna"),
    ("Portugal", "Lisbon"),
    ("Greece", "Athens"),
    ("Turkey", "Ankara"),
    ("Poland", "Warsaw"),
    ("Denmark", "Copenhagen"),
    ("Finland", "Helsinki"),
    ("Argentina", "Buenos Aires"),
    ("Chile", "Santiago"),
    ("Colombia", "Bogotá"),
    ("Peru", "Lima"),
    ("Nigeria", "Abuja"),
    ("Kenya", "Nairobi"),
    ("South Africa", "Pretoria"),
    ("New Zealand", "Wellington"),
    ("Indonesia", "Jakarta"),
    ("Iran", "Tehran"),
    ("Iraq", "Baghdad"),
    ("Saudi Arabia", "Riyadh"),
    ("Israel", "Jerusalem"),
    ("Lebanon", "Beirut"),
    ("Pakistan", "Islamabad"),
    ("Bangladesh", "Dhaka"),
    ("Vietnam", "Hanoi"),
    ("Malaysia", "Kuala Lumpur"),
    ("Singapore", "Singapore"),
    ("Ukraine", "Kyiv"),
    ("Czech Republic", "Prague"),
    ("Hungary", "Budapest"),
    ("Romania", "Bucharest"),
    ("Bulgaria", "Sofia")
]

# 10 variations for asking the capital question.
templates = [
    "What is the capital of {country}?",
    "Which city is the capital of {country}?",
    "Name the capital city of {country}.",
    "What city serves as the capital of {country}?",
    "Identify the capital of {country}.",
    "What is the administrative center of {country}?",
    "Provide the capital city of {country}.",
    "What is the seat of government in {country}?",
    "State the capital of {country}.",
    "Which city serves as the administrative capital of {country}?"
]

questions = []
# List of all capitals for generating distractors.
all_capitals = [capital for (_, capital) in country_capitals]

# For each country, create a question for each template.
for country, correct_capital in country_capitals:
    for template in templates:
        question_text = template.format(country=country)
        # Choose 3 random distractors that are not the correct answer.
        distractors = random.sample([cap for cap in all_capitals if cap != correct_capital], 3)
        options = distractors + [correct_capital]
        random.shuffle(options)
        correct_index = options.index(correct_capital)
        questions.append({
            "question": question_text,
            "options": options,
            "answer": correct_index
        })

# Ensure we have exactly 500 questions (50 countries * 10 templates).
print("Generated", len(questions), "questions.")

# Write the questions to a JSON file.
with open("geography_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=4, ensure_ascii=False)

print("geography_questions.json has been created with 500 actual geography questions.")
