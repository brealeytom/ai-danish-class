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

def get_available_models():
    api_key = load_api_key()
    
    url = "https://api.elevenlabs.io/v1/models"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            print("\nAvailable ElevenLabs Models:")
            print("-" * 50)
            
            for model in models:
                print(f"Name: {model['name']}")
                print(f"Model ID: {model['model_id']}")
                print(f"Description: {model.get('description', 'No description available')}")
                print(f"Languages: {', '.join(model.get('languages', ['Not specified']))}")
                print(f"Token limit: {model.get('token_limit', 'Not specified')}")
                print("-" * 50)
                
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the function
get_available_models()