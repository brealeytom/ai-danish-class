import os
import csv
import json
import hashlib
import requests
from dotenv import load_dotenv
from pydub import AudioSegment
from typing import Dict, Optional, TypedDict

class VoiceSettings(TypedDict):
    stability: float
    similarity_boost: float

class VoiceConfig(TypedDict):
    id: str
    settings: VoiceSettings

class VoiceMapper:
    def __init__(self):
        self.config_path = "resources/voice_config.json"
        # Create resources directory if it doesn't exist
        os.makedirs("resources", exist_ok=True)
        self.voice_map = self._load_config()

    def _load_config(self) -> Dict[str, VoiceConfig]:
        """Load voice mapping from config file, create default if doesn't exist"""
        if not os.path.exists(self.config_path):
            default_config = {
                "en_f_voice": {
                    "id": "pFZP5JQG7iQjIQuC4Bku",
                    "settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                },
                "da_f_voice": {
                    "id": "XB0fDUnXU5powFXDhCwa",
                    "settings": {
                        "stability": 0.7,
                        "similarity_boost": 0.8
                    }
                },
                "da_m_voice": {
                    "id": "IKne3meq5aSn9XLyUdCD",
                    "settings": {
                        "stability": 0.7,
                        "similarity_boost": 0.8
                    }
                }
            }
            self._save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _save_config(self, config: Dict[str, VoiceConfig]) -> None:
        """Save voice mapping to config file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def get_voice_id(self, csv_voice_id: str) -> Optional[str]:
        """Get ElevenLabs voice ID from CSV voice ID"""
        voice_config = self.voice_map.get(csv_voice_id)
        return voice_config["id"] if voice_config else None

    def get_voice_settings(self, csv_voice_id: str) -> Optional[VoiceSettings]:
        """Get voice settings for a specific voice"""
        voice_config = self.voice_map.get(csv_voice_id)
        return voice_config["settings"] if voice_config else None

    def list_voices(self) -> Dict[str, VoiceConfig]:
        """List all voice mappings and their settings"""
        return self.voice_map

def load_api_key():
    """Load API key from environment variable"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise ValueError("API key not found! Please set ELEVENLABS_API_KEY environment variable.")
    return api_key

def get_cache_filename(text, voice_id):
    """Generate a unique cache filename based on text and voice_id"""
    content_hash = hashlib.md5(f"{text}{voice_id}".encode()).hexdigest()
    return f"cache_{content_hash}.mp3"

def generate_speech(text, voice_id, output_filename, voice_mapper, cache_dir="audio_cache"): 
    """Generate speech and save to a specific filename, with caching"""
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Get the actual ElevenLabs voice ID and settings
    elevenlabs_voice_id = voice_mapper.get_voice_id(voice_id)
    voice_settings = voice_mapper.get_voice_settings(voice_id)
    
    if not elevenlabs_voice_id:
        raise ValueError(f"No ElevenLabs voice ID found for voice: {voice_id}")
    
    # Check cache first
    cache_filename = os.path.join(cache_dir, get_cache_filename(text, elevenlabs_voice_id))
    if os.path.exists(cache_filename):
        AudioSegment.from_mp3(cache_filename).export(output_filename, format="mp3")
        print(f"Using cached audio for '{text}'")
        return True
    
    # If not in cache, generate new audio
    api_key = load_api_key()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": voice_settings or {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save to cache
            with open(cache_filename, "wb") as f:
                f.write(response.content)
            # Copy to output filename
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"Audio file generated and cached as '{cache_filename}'")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def split_audio_file(audio, chunk_duration_ms, output_folder):
    """Split audio into smaller chunks"""
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_duration_ms)):
        end = start + chunk_duration_ms
        chunk = audio[start:end]
        chunk_filename = os.path.join(output_folder, f"chunk_{i + 1}.mp3")
        chunk.export(chunk_filename, format="mp3")
        chunks.append(chunk_filename)
    return chunks

def process_csv_to_audio(csv_filename, output_filename, chunk_duration_sec=600):
    """Process a CSV file and create a combined audio file with handling for large files"""
    temp_files = []
    output_folder = "output_chunks"
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize voice mapper
    voice_mapper = VoiceMapper()
    print("Loaded voice configurations:")
    print(json.dumps(voice_mapper.list_voices(), indent=2))
    
    try:
        # Read CSV and sort by order_id
        with open(csv_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            entries = sorted(reader, key=lambda x: int(x['order_id']))
        
        if not entries:
            print("CSV file is empty")
            return False
        
        combined = AudioSegment.silent(duration=0)
        
        # Process each entry
        for i, entry in enumerate(entries):
            temp_filename = f"temp_{i}.mp3"
            temp_files.append(temp_filename)
            
            # Generate speech with voice mapper
            if not generate_speech(
                entry['text'], 
                entry['voice_id'], 
                temp_filename,
                voice_mapper
            ):
                return False
            
            # Load the audio segment
            current_segment = AudioSegment.from_mp3(temp_filename)
            
            # Add the segment the number of times specified in the repeat column
            repeat_count = int(entry.get('repeat', 1))
            for _ in range(repeat_count):
                combined += current_segment
                
                # Add pause after each repetition
                pause_duration = int(float(entry['delay']))
                if pause_duration > 0:
                    combined += AudioSegment.silent(duration=pause_duration)
        
        # Check total duration for splitting
        max_duration_ms = chunk_duration_sec * 1000
        if len(combined) > max_duration_ms:
            print("Audio file exceeds size limit. Splitting into smaller chunks...")
            chunks = split_audio_file(combined, max_duration_ms, output_folder)
            print(f"Audio split into {len(chunks)} chunks, saved in '{output_folder}'.")
        else:
            combined.export(output_filename, format="mp3")
            print(f"Final audio saved as '{output_filename}'")
        
        return True
        
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return False
        
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

# Example usage
if __name__ == "__main__":
    # Test voice mapper
    voice_mapper = VoiceMapper()
    print("Current voice configurations:")
    print(json.dumps(voice_mapper.list_voices(), indent=2))
    
    # Process CSV file
    process_csv_to_audio(
        "lessons/lesson_3_3/02_role_playing_section.csv", 
        "lessons/lesson_3_3/test_danish_voice_script.mp3", 
        chunk_duration_sec=600
    )