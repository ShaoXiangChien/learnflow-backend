import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_quiz(transcript: str, language: str, num_questions: int = 5):
    """
    Generate a quiz based on video transcript using OpenAI GPT-4
    """
    prompt = f"""You are a language learning assistant. Based on the following {language} transcript,
generate {num_questions} multiple choice questions to test comprehension and vocabulary.

Transcript:
{transcript}

Requirements:
- Questions should test vocabulary, grammar, and comprehension
- Each question should have 4 options
- Include one correct answer (index 0-3)
- Provide a brief explanation for the correct answer
- Make questions appropriate for language learners
- Mix question types: vocabulary, comprehension, and grammar

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "What does 'palabra' mean?",
    "options": ["Word", "Phrase", "Sentence", "Letter"],
    "correct_answer": 0,
    "explanation": "'Palabra' means 'word' in English."
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful language learning assistant that generates quiz questions. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        questions = json.loads(content)
        return questions

    except Exception as e:
        print(f"Error generating quiz: {e}")
        # Return fallback questions
        return [
            {
                "question": "What is the main topic of this video?",
                "options": ["Food and markets", "Sports", "Technology", "Travel"],
                "correct_answer": 0,
                "explanation": "The video discusses food and markets."
            }
        ]


def translate_word(text: str, from_lang: str, to_lang: str):
    """
    Translate a word or phrase using OpenAI
    """
    prompt = f"""Translate this {from_lang} text to {to_lang}: "{text}"

Provide:
1. Translation
2. Pronunciation (IPA or phonetic)
3. A brief definition
4. An example sentence in {from_lang}

Return as JSON:
{{
  "translation": "...",
  "pronunciation": "...",
  "definition": "...",
  "example": "..."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a language translation assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)
        return result

    except Exception as e:
        print(f"Error translating: {e}")
        return {
            "translation": text,
            "pronunciation": "",
            "definition": "",
            "example": ""
        }
