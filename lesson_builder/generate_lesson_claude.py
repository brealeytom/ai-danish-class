import anthropic
import json
import os
from typing import Dict, Any
from pathlib import Path
from prompt_manager import PromptManager

def create_danish_lesson(lesson_data: Dict[str, Any], prompt_type: str, prompt_manager: PromptManager) -> str:
    """
    Creates a Danish lesson using Claude API.
    
    Args:
        lesson_data: Dictionary containing lesson number, title, and target phrases
        prompt_type: Type of prompt to use
        prompt_manager: Instance of PromptManager
    """
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
    
    # Get formatted prompt and examples
    system_prompt, examples = prompt_manager.format_for_claude(prompt_type)
    
    # Create the complete message content
    message_content = [
        {
            "type": "text",
            "text": examples
        },
        {
            "type": "text",
            "text": json.dumps(lesson_data)
        }
    ]

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": message_content
            }
        ]
    )
    
    # Handle the response content - get the text from the first content item
    if isinstance(message.content, list) and len(message.content) > 0:
        # Assuming the first content item contains the CSV data
        first_content = message.content[0]
        if hasattr(first_content, 'text'):
            return first_content.text
        elif isinstance(first_content, dict) and 'text' in first_content:
            return first_content['text']
    
    raise ValueError("Unexpected response format from Claude")

def process_lessons_from_config(
    config_path: str,
    output_dir: str = "lessons",
    prompts_dir: str = "lesson_builder/prompts"
) -> None:
    """
    Reads lessons from config file and generates CSV files in specified order.
    """
    prompt_manager = PromptManager(prompts_dir)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    lessons = config["lessons"]
    print(f"Found {len(lessons)} lessons in config file")
    
    for i, lesson in enumerate(lessons, 1):
        lesson_num = lesson['lesson_number']
        print(f"\nProcessing lesson {lesson_num} ({i}/{len(lessons)})")
        
        lesson_dir = Path(output_dir) / f"lesson_{str(lesson_num).replace('.', '_')}"
        lesson_dir.mkdir(exist_ok=True)
        
        # Sort prompt sequence by order if needed (though JSON array order is preserved)
        prompt_sequence = sorted(lesson['prompt_sequence'], key=lambda x: x['order'])
        
        # Process each prompt type in sequence
        for prompt_config in prompt_sequence:
            prompt_type = prompt_config['type']
            try:
                print(f"  Generating {prompt_type} version (step {prompt_config['order']})...")
                print(f"  Description: {prompt_config['description']}")
                
                csv_content = create_danish_lesson(lesson, prompt_type, prompt_manager)
                
                # Create numbered filename to maintain order
                filename = f"{prompt_config['order']:02d}_{prompt_type}.csv"
                filepath = lesson_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(csv_content)
                    
                print(f"  Successfully generated {filename}")
                
            except Exception as e:
                print(f"  Error processing {prompt_type} version: {str(e)}")
                continue

if __name__ == "__main__":
    config_path = "resources/lessons_config.json"
    
    # Process lessons from config file
    process_lessons_from_config(config_path)