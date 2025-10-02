```markdown
# Danish Language Learning Course Builder

A Python-based pipeline for generating structured Danish language lessons with AI-generated content and text-to-speech audio.

## Overview

This repository contains a complete system for building language learning courses. It takes structured lesson content, generates daily lesson plans, creates pedagogically-sound lesson transcripts using Claude AI, and produces audio files using ElevenLabs text-to-speech.

## Architecture

The system consists of four main components:

1. **Daily Plan Generator** (`generate_daily_plans.py`) - Creates structured daily lesson plans from configuration files
2. **Transcript Generator** (`generate_transcripts.py`) - Uses Claude AI to generate lesson transcripts
3. **Audio Generator** (`generate_audio.py`) - Converts transcripts to audio using ElevenLabs
4. **Prompt Manager** (`prompt_manager.py`) - Manages AI prompts and examples for different lesson types

## Project Structure

```
├── resources/
│   ├── lessons_content_config.json    # Lesson content and phrases
│   ├── weekly_structure_config.json   # Daily lesson structure
│   └── voice_config.json              # TTS voice configurations
├── lesson_builder/
│   └── prompts/                       # Prompt configurations for Claude
│       ├── [activity_type]/
│       │   ├── metadata.yaml
│       │   ├── system_prompt.md
│       │   └── examples/
│       │       └── *.json
└── danish/                            # Generated course content
    └── part_XX/
        └── lesson_XX/
            ├── daily_plans/           # JSON lesson plans
            ├── daily_transcripts/     # CSV transcripts
            ├── audio/                 # Individual audio files
            └── combined_audio/        # Combined daily audio
```

## Installation

```bash
pip install anthropic pydub requests python-dotenv pyyaml
```

### Environment Variables

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_claude_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Usage

### 1. Generate Daily Plans

Creates structured lesson plans from your configuration files:

```bash
python generate_daily_plans.py
```

**Input:** 
- `resources/lessons_content_config.json` - Defines phrases and content for each lesson
- `resources/weekly_structure_config.json` - Defines the structure of daily lessons

**Output:** 
- `danish/part_XX/lesson_XX/daily_plans/XX_[day].json` - Daily lesson plans

### 2. Generate Transcripts

Uses Claude AI to create lesson transcripts based on the daily plans:

```bash
# Generate all transcripts
python generate_transcripts.py

# Test mode (skip API calls)
python generate_transcripts.py --test

# Specify custom base directory
python generate_transcripts.py --base-dir path/to/course
```

**Features:**
- Skips existing files to avoid overwriting
- Generates multiple activity types per day (warmup, presentation, practice, etc.)
- Uses configurable prompts for different lesson activities

**Output:** 
- `danish/part_XX/lesson_XX/daily_transcripts/[day]_XX_[activity].csv` - Lesson transcripts

### 3. Generate Audio

Converts transcripts to audio using ElevenLabs TTS:

```bash
python generate_audio.py
```

**Key Functions:**

```python
# Process entire directory structure
process_directory("danish", part="part_01", lesson="lesson_01")

# Combine audio files for a complete day
combine_lesson_audio("danish", "part_01", "lesson_01")

# Test mode (generates text summaries instead of audio)
process_directory("danish", test_mode=True)
```

**Features:**
- Audio caching to avoid regenerating identical segments
- Voice mapping with customizable settings (stability, similarity)
- Automatic file splitting for large audio files
- Combines multiple audio segments into complete daily lessons

## Configuration Files

### lessons_content_config.json

Defines the course structure and content:

```json
{
  "lessons": [
    {
      "lesson_number": 1.1,
      "title": "Greetings",
      "target_phrases": [
        {
          "danish": "Hej",
          "english": "Hello",
          "modifications": [...]
        }
      ]
    }
  ]
}
```

### weekly_structure_config.json

Defines how lessons are structured across days:

```json
{
  "lessons": [
    {
      "day": "Monday",
      "target_phrases": [1, 2, 3],
      "recap_phrases": [],
      "lesson_structure": ["warmup", "presentation", "practice"]
    }
  ]
}
```

### voice_config.json

Maps voice IDs to ElevenLabs voices with custom settings:

```json
{
  "en_f_voice": {
    "id": "elevenlabs_voice_id",
    "settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }
}
```

## Prompt Management

The `PromptManager` class handles AI prompts for different lesson activities:

```python
from prompt_manager import PromptManager

pm = PromptManager("lesson_builder/prompts")

# Get formatted prompt for Claude API
system_prompt, examples = pm.format_for_claude("warmup")

# List available prompt types
prompt_types = pm.list_prompt_types()
```

**Prompt Directory Structure:**
```
prompts/
└── warmup/
    ├── metadata.yaml           # Name and description
    ├── system_prompt.md        # Instructions for Claude
    └── examples/
        └── example_01.json     # Input/output examples
```

## CSV Transcript Format

Generated transcripts follow this format:

```csv
order_id,voice_id,text,repeat,delay
1,en_f_voice,"Welcome to the lesson",1,1000
2,da_f_voice,"Hej",2,2000
3,en_f_voice,"That means hello",1,1000
```

**Fields:**
- `order_id` - Playback order
- `voice_id` - Voice identifier (mapped in voice_config.json)
- `text` - Text to speak
- `repeat` - Number of repetitions
- `delay` - Pause duration after speech (milliseconds)

## Test Mode

All scripts support test mode for development without API calls:

```bash
python generate_transcripts.py --test
python generate_audio.py  # Set test_mode=True in script
```

Test mode creates text files instead of making API calls or generating audio, useful for:
- Debugging prompt configurations
- Validating lesson structure
- Testing without API costs

## Features

- **Intelligent Caching**: Audio segments are cached to avoid regenerating identical content
- **Incremental Processing**: Skips existing files to enable resumable processing
- **Flexible Voice Control**: Per-voice settings for natural-sounding speech
- **Modular Prompts**: Easy-to-update prompt system for different activity types
- **Error Handling**: Continues processing despite individual failures
- **Test Mode**: Develop without API costs

## Best Practices

1. **Start with test mode** to validate your configuration before generating audio
2. **Use version control** for your prompt configurations
3. **Cache directory** can grow large - periodically clean unused cached audio
4. **Monitor API usage** - Claude and ElevenLabs calls can add up quickly
5. **Backup configurations** before making structural changes

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
```