import json
from pathlib import Path
from typing import List, Dict, Any

def load_configs() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load both configuration files."""
    with open('resources/lessons_content_config.json', 'r', encoding='utf-8') as f:
        content_config = json.load(f)
    
    with open('resources/weekly_structure_config.json', 'r', encoding='utf-8') as f:
        structure_config = json.load(f)
    
    return content_config, structure_config

def get_phrases_by_indices(phrases: List[Dict[str, str]], indices: List[int]) -> List[Dict[str, str]]:
    """Get phrases by their 1-based indices."""
    return [phrases[i-1] for i in indices]

def parse_lesson_number(lesson_number: float) -> tuple[int, int]:
    """Convert lesson number (e.g., 1.1) to part and lesson numbers."""
    part_num, lesson_num = str(lesson_number).split('.')
    return int(part_num), int(lesson_num)

def generate_daily_lesson_plans(
    content_config: Dict[str, Any], 
    structure_config: Dict[str, Any], 
    base_dir: str = "danish"
) -> None:
    """
    Generates daily lesson plans for each lesson in the course.
    
    Args:
        content_config: Dictionary containing course and lesson content
        structure_config: Dictionary containing the weekly lesson structure
        base_dir: Base directory for lessons
    """
    base_path = Path(base_dir)
    
    # Process each lesson
    for lesson in content_config["lessons"]:
        lesson_number = lesson["lesson_number"]
        part_num, lesson_num = parse_lesson_number(lesson_number)
        title = lesson["title"]
        all_phrases = lesson["target_phrases"]
        
        # Create lesson directory path with new structure
        lesson_dir = (base_path / 
                     f"part_{part_num:02d}" / 
                     f"lesson_{lesson_num:02d}" /
                     "daily_plans")
        
        # Create directories
        lesson_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each day's lesson
        for i, daily_lesson in enumerate(structure_config["lessons"], 1):
            day = daily_lesson["day"].lower()
            
            # Get specific phrases for this day
            target_phrases = get_phrases_by_indices(all_phrases, daily_lesson["target_phrases"])
            recap_phrases = get_phrases_by_indices(all_phrases, daily_lesson["recap_phrases"])
            
            # Create the daily lesson plan
            daily_plan = {
                "lesson_number": lesson_number,
                "title": title,
                "day": daily_lesson["day"],
                "recap_phrases": recap_phrases,
                "target_phrases": target_phrases,
                "lesson_structure": daily_lesson["lesson_structure"]
            }
            
            # Save to file with new naming convention
            filepath = lesson_dir / f"{i:02d}_{day}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(daily_plan, f, ensure_ascii=False, indent=2)
            
            print(f"Generated {day} plan for Part {part_num}, Lesson {lesson_num}")
            print(f"  → Saved to: {filepath}")

def main():
    # Load both config files
    content_config, structure_config = load_configs()
    
    # Generate daily plans
    generate_daily_lesson_plans(content_config, structure_config)
    
    print("\nDaily lesson plans generated successfully!")

if __name__ == "__main__":
    main()