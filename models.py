from pydantic import BaseModel
from typing import List, Optional


class Word(BaseModel):
    word: str
    translation: str
    pronunciation: str
    definition: Optional[str] = None
    example: Optional[str] = None


class Subtitle(BaseModel):
    start: float
    end: float
    text_target: str
    text_native: str
    words: List[Word]


class Video(BaseModel):
    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    language: str
    difficulty: str
    duration: int
    description: Optional[str] = None
    subtitles: List[Subtitle]
    quiz: Optional['Quiz'] = None


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


class Quiz(BaseModel):
    video_id: str
    questions: List[QuizQuestion]


class QuizGenerateRequest(BaseModel):
    video_id: str
    transcript: str
    language: str


class TranslateRequest(BaseModel):
    text: str
    from_lang: str
    to_lang: str


class TranslateResponse(BaseModel):
    translation: str
    pronunciation: Optional[str] = None
