from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn
import os

from models import (
    Video, Quiz, QuizGenerateRequest,
    TranslateRequest, TranslateResponse
)
from services.video_service import (
    get_all_videos, get_video_by_id, get_video_transcript, save_quiz_to_video, get_video_quiz
)
from services.openai_service import generate_quiz, translate_word

app = FastAPI(title="LearnFlow API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create videos directory if it doesn't exist
os.makedirs("videos", exist_ok=True)

# Serve static video files
if os.path.exists("videos"):
    app.mount("/videos", StaticFiles(directory="videos"), name="videos")


@app.get("/")
def read_root():
    return {"message": "Welcome to LearnFlow API"}


@app.get("/api/videos", response_model=List[Video])
def list_videos():
    """Get all available videos"""
    videos = get_all_videos()
    return videos


@app.get("/api/videos/{video_id}", response_model=Video)
def get_video(video_id: str):
    """Get a specific video with subtitles"""
    video = get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@app.get("/api/videos/{video_id}/quiz", response_model=Quiz)
def get_quiz(video_id: str):
    """Get quiz for a video - generate if not exists"""
    try:
        # Check if quiz already exists
        existing_quiz = get_video_quiz(video_id)
        if existing_quiz:
            return existing_quiz
        
        # Get video and transcript
        video = get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        transcript = get_video_transcript(video_id)
        if not transcript:
            raise HTTPException(status_code=404, detail="Video transcript not found")
        
        # Generate quiz using OpenAI
        questions = generate_quiz(transcript, video.language)
        quiz = Quiz(video_id=video_id, questions=questions)
        
        # Save quiz to video data
        save_quiz_to_video(video_id, quiz)
        
        return quiz
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@app.post("/api/quiz/generate", response_model=Quiz)
def create_quiz(request: QuizGenerateRequest):
    """Generate a quiz for a video (legacy endpoint)"""
    try:
        # Get transcript if not provided
        transcript = request.transcript
        if not transcript:
            transcript = get_video_transcript(request.video_id)

        if not transcript:
            raise HTTPException(status_code=404, detail="Video transcript not found")

        # Generate quiz using OpenAI
        questions = generate_quiz(transcript, request.language)
        quiz = Quiz(video_id=request.video_id, questions=questions)
        
        # Save quiz to video data
        save_quiz_to_video(request.video_id, quiz)

        return quiz

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")



@app.post("/api/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest):
    """Translate a word or phrase"""
    try:
        result = translate_word(request.text, request.from_lang, request.to_lang)
        return TranslateResponse(
            translation=result.get("translation", ""),
            pronunciation=result.get("pronunciation", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
