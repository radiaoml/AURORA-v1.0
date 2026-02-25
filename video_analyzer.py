import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
import cv2
import os
import json
import time
from gemini_vision_client import GeminiVisionClient

import yt_dlp

class TacticalVisionEngine:
    def __init__(self, source):
        self.source = source # Can be a URL, local path, or upload buffer
        self.is_url = source.startswith('http')
        self.output_dir = "frames_buffer"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_tactical_frames(self, fps_sample=1):
        """Extracts key frames for the Multimodal LLM to analyze."""
        source_type = "CLOUD_STREAM" if self.is_url else "LOCAL_BUFFER"
        print(f"--- ANALYZING {source_type}: {self.source} ---")
        
        # Meta-extraction for Dynamic Reasoning
        source_meta = self.source if not self.is_url else f"YT_{self.source}"
        
        video_path = self.source
        
        if self.is_url:
            print(f"[INFO] DOWNLOADING YouTube video from: {self.source}")
            print("[INFO] This may take a few seconds...")
            
            # Download video using yt-dlp
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]', # Prefer 720p mp4 to avoid massive files and ffmpeg merging
                'outtmpl': 'frames_buffer/temp_vod.%(ext)s',
                'quiet': False, # ENABLE OUTPUT to see what's happening
                'no_warnings': False,
                'force_overwrites': True
            }
            
            try:
                import yt_dlp
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.source])
                video_path = f"{self.output_dir}/temp_vod.mp4"
                print(f"[SUCCESS] Video downloaded to {video_path}")
            except Exception as e:
                print(f"\n[ERROR] YOUTUBE DOWNLOAD FAILED: {e}")
                print("[ERROR] Please ensure ffmpeg is installed if merging is required.")
                print(f"[ERROR] Falling back to mock data.\n")
                return [], source_meta

        # Standard OpenCV Extraction (works for both local files and downloaded videos)
        if not os.path.exists(video_path):
             print(f"[ERROR] Video file not found: {video_path}")
             return [], source_meta
             
        vidcap = cv2.VideoCapture(video_path)
        if not vidcap.isOpened():
             print(f"[ERROR] Failed to open video: {video_path}")
             return [], source_meta

        success, image = vidcap.read()
        count = 0
        extracted = []
        
        # Calculate frame skip interval based on FPS
        fps = vidcap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = int(fps / fps_sample) if fps_sample > 0 else 30
        
        while success:
            if count % frame_interval == 0: 
                frame_name = f"{self.output_dir}/frame_{len(extracted)}.jpg"
                cv2.imwrite(frame_name, image)
                extracted.append(frame_name)
                
                # Limit to 10 frames to avoid overloading Gemini API and speed up processing
                if len(extracted) >= 10:
                    break
                    
            success, image = vidcap.read()
            count += 1
            
        vidcap.release()
            
        print(f"[SUCCESS] Extracted {len(extracted)} tactical snapshots for analysis.")
        return extracted, source_meta

    def get_multimodal_critique(self, frames, source_meta="Unknown"):
        """
        Bridges to Gemini 1.5 Pro for real-match visual reasoning.
        """
        client = GeminiVisionClient()
        print(f"[VISION] Handing off {len(frames)} frames to the Neural Engine...")
        
        # In a real production environment, we would upload the video or send frames
        return client.analyze_gameplay_vod(frames, source_info=source_meta)

if __name__ == "__main__":
    # Simulate a VOD review session
    # engine = TacticalVisionEngine("valorant_match_vod.mp4")
    # frames = engine.extract_tactical_frames()
    # critique = engine.get_multimodal_critique(frames)
    print("VOD Engine ready for high-precision visual analysis.")
