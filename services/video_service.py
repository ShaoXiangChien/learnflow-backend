import json
from typing import List, Optional
from models import Video, Quiz


def load_videos() -> List[Video]:
    """Load videos from JSON file"""
    try:
        with open('data/videos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Video(**video) for video in data['videos']]
    except Exception as e:
        print(f"Error loading videos: {e}")
        return []


def get_all_videos() -> List[Video]:
    """Get all available videos"""
    return load_videos()


def get_video_by_id(video_id: str) -> Optional[Video]:
    """Get a specific video by ID"""
    videos = load_videos()
    for video in videos:
        if video.id == video_id:
            return video
    return None


def get_video_transcript(video_id: str) -> str:
    """Extract full transcript from video subtitles"""
    video = get_video_by_id(video_id)
    if not video:
        return ""

    transcript_parts = [sub.text_target for sub in video.subtitles]
    return " ".join(transcript_parts)


def save_quiz_to_video(video_id: str, quiz: Quiz) -> bool:
    """Save quiz to video data in JSON file"""
    try:
        with open('data/videos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find and update the video
        for video in data['videos']:
            if video['id'] == video_id:
                video['quiz'] = {
                    'video_id': quiz.video_id,
                    'questions': [
                        {
                            'question': q.question,
                            'options': q.options,
                            'correct_answer': q.correct_answer,
                            'explanation': q.explanation
                        }
                        for q in quiz.questions
                    ]
                }
                break
        
        # Write back to file
        with open('data/videos.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving quiz: {e}")
        return False


def get_video_quiz(video_id: str) -> Optional[Quiz]:
    """Get quiz from video data"""
    video = get_video_by_id(video_id)
    if not video:
        return None
    
    return video.quiz
