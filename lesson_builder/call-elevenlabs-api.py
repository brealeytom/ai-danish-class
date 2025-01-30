import os
import csv
import requests
from dotenv import load_dotenv
from pydub import AudioSegment

def load_api_key():
    """Load API key from environment variable"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise ValueError("API key not found! Please set ELEVENLABS_API_KEY environment variable.")
    return api_key

def generate_speech(text, voice_id, output_filename): 
    """Generate speech and save to a specific filename"""
    api_key = load_api_key()
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"Audio file generated successfully as '{output_filename}'")
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
    os.makedirs(output_folder, exist_ok=True)  # Create output folder for chunks
    
    try:
        # Read CSV and sort by order_id
        with open(csv_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            entries = sorted(reader, key=lambda x: int(x['order_id']))
        
        if not entries:
            print("CSV file is empty")
            return False
        
        combined = AudioSegment.silent(duration=0)  # Initialize combined audio
        
        # Process each entry
        for i, entry in enumerate(entries):
            temp_filename = f"temp_{i}.mp3"
            temp_files.append(temp_filename)  # Track temporary files
            
            # Generate speech
            if not generate_speech(entry['text'], entry['voice_id'], temp_filename):
                return False
            
            # Add current audio segment
            current_segment = AudioSegment.from_mp3(temp_filename)
            combined += current_segment
            
            # Add pause if specified
            pause_duration = int(float(entry['delay']))  # Convert to milliseconds
            if pause_duration > 0:
                combined += AudioSegment.silent(duration=pause_duration)
        
        # Check total duration for splitting
        max_duration_ms = chunk_duration_sec * 1000  # Convert to milliseconds
        if len(combined) > max_duration_ms:
            print("Audio file exceeds size limit. Splitting into smaller chunks...")
            chunks = split_audio_file(combined, max_duration_ms, output_folder)
            print(f"Audio split into {len(chunks)} chunks, saved in '{output_folder}'.")
        else:
            # Export as a single file if under the size limit
            combined.export(output_filename, format="mp3")
            print(f"Final audio saved as '{output_filename}'")
        
        return True
        
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return False
        
    finally:
        # Ensure temporary files are cleaned up
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

# Example usage
if __name__ == "__main__":
    process_csv_to_audio("lesson_builder/lesson_transcripts/lesson_2_work_and_studies.csv", "lesson_builder/lesson_audio/final_output.mp3", chunk_duration_sec=600)  # Adjust chunk size as needed
