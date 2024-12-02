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

def process_csv_to_audio(csv_filename, output_filename="final_output.mp3"):
    """Process a CSV file and create a combined audio file"""
    try:
        # Read CSV and sort by order_id
        with open(csv_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            entries = sorted(reader, key=lambda x: int(x['order_id']))
        
        # Generate initial audio file from first entry
        if not entries:
            print("CSV file is empty")
            return False
        
        # Generate first audio segment
        first_entry = entries[0]
        if not generate_speech(first_entry['text'], first_entry['voice_id'], "temp_0.mp3"):
            return False
        
        combined = AudioSegment.from_mp3("temp_0.mp3")
        os.remove("temp_0.mp3")  # Clean up temporary file
        
        # Add pause after first entry
        pause_duration = int(float(first_entry['after_pause_len']))  # Convert to milliseconds
        if pause_duration > 0:
            combined += AudioSegment.silent(duration=pause_duration)
        
        # Process remaining entries
        for i, entry in enumerate(entries[1:], 1):
            # Generate speech for current entry
            temp_filename = f"temp_{i}.mp3"
            if not generate_speech(entry['text'], entry['voice_id'], temp_filename):
                return False
            
            # Add current audio segment
            current_segment = AudioSegment.from_mp3(temp_filename)
            combined += current_segment
            
            # Clean up temporary file
            os.remove(temp_filename)
            
            # Add pause if specified
            pause_duration = int(float(entry['after_pause_len']) * 1000)  # Convert to milliseconds
            if pause_duration > 0:
                combined += AudioSegment.silent(duration=pause_duration)
        
        # Export final combined audio
        combined.export(output_filename, format="mp3")
        print(f"Final audio saved as '{output_filename}'")
        return True
        
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    process_csv_to_audio("input.csv")