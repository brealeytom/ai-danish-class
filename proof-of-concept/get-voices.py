import os
import requests
from dotenv import load_dotenv

def load_api_key():
    """Load API key from environment variable"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise ValueError("API key not found! Please set ELEVENLABS_API_KEY environment variable.")
    return api_key

def get_available_voices():
    api_key = load_api_key()
    
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()["voices"]
            print("\nVoices that support Danish:")
            print("-" * 50)
            for voice in voices: 
                language = voice.get("labels", {}).get("languages", [])
                print  
            for voice in voices:
                # Check if the voice supports Danish (language code 'da')
                if "de" in [lang.get("language_id") for lang in voice.get("labels", {}).get("languages", [])]:
                    print(f"Name: {voice['name']}")
                    print(f"Voice ID: {voice['voice_id']}")
                    print(f"Description: {voice.get('description', 'No description available')}")
                    print("-" * 50)
                    
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the function
get_available_voices()