import anthropic
import json
import os
from typing import Dict, Any
from pathlib import Path
from prompt_manager import PromptManager

def create_danish_lesson(lesson_data: Dict[str, Any], prompt_type: str, prompt_manager: PromptManager, test_mode: bool = False) -> str:
    """
    Creates a Danish lesson using Claude API.
    
    Args:
        lesson_data: Dictionary containing lesson data including day, title, and phrases
        prompt_type: Type of prompt to use
        prompt_manager: Instance of PromptManager
    """
    # Filter lesson data to include only necessary fields
    filtered_data = {
        "title": lesson_data["title"],
        "recap_phrases": lesson_data["recap_phrases"],
        "target_phrases": lesson_data["target_phrases"]
    }
    
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
    
    # Get formatted prompt and examples
    system_prompt, examples = prompt_manager.format_for_claude(prompt_type)
    
    # If in test mode, return debug content
    if test_mode:
        print(f"TEST MODE: Skipping API call for {prompt_type}")
        debug_output = [
            "=== System Prompt ===",
            system_prompt,
            "\n=== Examples ===",
            examples,
            "\n=== Input Data ===",
            json.dumps(filtered_data, ensure_ascii=False, indent=2)
        ]
        return "\n".join(debug_output)
    
    # Create the complete message content
    message_content = [
        {
            "type": "text",
            "text": examples
        },
        {
            "type": "text",
            "text": json.dumps(filtered_data, ensure_ascii=False, indent=2)
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
    
    if isinstance(message.content, list) and len(message.content) > 0:
        first_content = message.content[0]
        if hasattr(first_content, 'text'):
            return first_content.text
        elif isinstance(first_content, dict) and 'text' in first_content:
            return first_content['text']
    
    raise ValueError("Unexpected response format from Claude")

def process_daily_plan(
    plan_file: Path,
    prompts_dir: str = "lesson_builder/prompts",
    test_mode: bool = False
) -> None:
    """
    Process a single daily plan file and generate outputs for each activity type.
    Skip files that already exist instead of overwriting them.
    
    Args:
        plan_file: Path to the daily plan JSON file
        prompts_dir: Directory containing prompt configurations
    """
    prompt_manager = PromptManager(prompts_dir)
    
    # Load lesson data
    with open(plan_file, 'r', encoding='utf-8') as f:
        lesson_data = json.load(f)
    
    # Determine paths based on the plan file location
    lesson_dir = plan_file.parent.parent  # Go up from daily_plans to lesson_01
    transcripts_dir = lesson_dir / "daily_transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    
    # Get day from filename (e.g., "tuesday" from "tuesday_02.json")
    day = plan_file.stem.split('_')[0].lower()
    
    # Process each activity type in the lesson structure
    for idx, activity_type in enumerate(lesson_data['lesson_structure'], 1):
        try:
            # Create filename using the day and activity
            filename = f"{day}_{idx:02d}_{activity_type}.csv"
            filepath = transcripts_dir / filename
            
            # Skip if file already exists
            if filepath.exists():
                print(f"  Skipping {filename} - file already exists")
                continue
                
            print(f"  Generating {activity_type} version...")
            csv_content = create_danish_lesson(lesson_data, activity_type, prompt_manager, test_mode=test_mode)
            
            # Write new content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(csv_content)
                
            print(f"  Successfully generated {filename}")
            
        except Exception as e:
            print(f"  Error processing {activity_type} version: {str(e)}")
            continue

def process_lesson_plans(base_dir: str = "danish", test_mode: bool = False) -> None:
    """
    Process all daily plan files in the Danish course structure.
    
    Args:
        base_dir: Base directory for the Danish course
    """
    base_path = Path(base_dir)
    
    # Find all daily plan JSON files
    plan_files = base_path.glob("**/daily_plans/*.json")
    
    for plan_file in sorted(plan_files):
        print(f"\nProcessing daily plan: {plan_file.relative_to(base_path)}")
        process_daily_plan(plan_file, test_mode=test_mode)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Danish lesson transcripts')
    parser.add_argument('--test', action='store_true', help='Run in test mode (skip API calls)')
    parser.add_argument('--base-dir', default='danish', help='Base directory for Danish course')
    
    args = parser.parse_args()
    
    # Process all daily plans
    process_lesson_plans(base_dir=args.base_dir, test_mode=args.test)