import json
import csv
import os
import requests

def call_claude_api(prompt, lesson_json, api_key):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Anthropic-Version": "2023-06-01"
    }
    
    data = {
        "model": "claude-3.5-sonnet",
        "max_tokens": 1024,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": prompt + "\n\n" + json.dumps(lesson_json)}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"]

def save_csv(output_text, filename):
    rows = [line.split(',') for line in output_text.strip().split('\n')]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def load_prompt(prompt_filename):
    prompt_path = os.path.join("prompts", prompt_filename)
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def load_lessons():
    with open("lesson_structure.json", "r", encoding="utf-8") as file:
        return json.load(file)

def main():
    api_key = os.getenv("CLAUDE_API_KEY")  # Store API key in environment variable
    
    lessons = load_lessons()
    prompt_filename = "default_prompt.txt"  # Change to select a different prompt
    prompt = load_prompt(prompt_filename)
    
    for lesson in lessons:
        lesson_number = lesson["lesson_number"]
        output_text = call_claude_api(prompt, lesson, api_key)
        csv_filename = f"lesson_{lesson_number}.csv"
        save_csv(output_text, csv_filename)
        print(f"CSV file saved as {csv_filename}")
    
if __name__ == "__main__":
    main()