# Task  
You will receive a `lesson_section` json object. Create a structured Danish language lesson in json format optimized for **audio lesson generation**, following **Pimsleur methodology** and specific timing rules.

---

# Output Format  
Generate a CSV with the following columns:  
- **`segment_id`**: Identifier for lesson segment (e.g., introduction, new_content, practice, review).  
- **`order_id`**: Sequential order within the lesson.  
- **`language`**: "en" for English, "da" for Danish.  
- **`voice_id`**: "en_voice" or "da_voice" for speaker assignment.  
- **`text`**: The spoken content.  
- **`delay`**: Pause duration in milliseconds (1000–4000ms).

---

# Lesson Requirements  

## Language Distribution  
- Use the Danish/English ratio specified in the Markdown object (e.g., 20% Danish, 80% English for basic lessons).  
- Gradually increase Danish content throughout the lesson.

## Repetition Rules  
- Teach each target phrase with **4 repetitions**, followed by **3 additional practice repetitions**.  
- Gradually increase pause durations between repetitions.

## Dialogue Practice  
- Include **English translations** before Danish practice phrases during the initial teaching phase.  
- Add **pause durations** to allow time for student responses.  
- Build dialogues progressively from individual phrases to complete conversations.

---

# Timing Guidelines  

### Pause Categories  
- **Short Pause (1000ms):** After English instructions or explanations.  
- **Medium Pause (2000ms):** Before student responses or repetitions.  
- **Long Pause (3000–4000ms):** During complex phrases, dialogues, or final practice.  

### Voice Selection  
- Use `en_voice` for:  
  - Instructions, English translations, and explanatory content.  
- Use `da_voice` for:  
  - Danish vocabulary, phrases, pronunciation, and dialogues.  
  - Split rows to isolate Danish words embedded in English sentences.

---

# Example CSV Output  

```csv
segment_id,order_id,language,voice_id,text,delay
1,introduction,en,en_voice,"Welcome to Lesson 1: First Meetings",1000
2,introduction,en,en_voice,"Today, we'll learn basic Danish greetings. Listen to this conversation:",1500
3,introduction_conversation,da,da_voice,"Hej, hvad hedder du?",1000
4,introduction_conversation,da,da_voice,"Hej, jeg hedder Henrik.",1000
5,new_content,da,da_voice,"Hej",2000
6,new_content,en,en_voice,"It means 'Hello'. Repeat after me.",1500
7,new_content,da,da_voice,"Hej",2000
```

## CSV Validation Rules
1. No blank rows allowed
2. All columns must be filled
3. segment_id must match row ranges exactly
4. order_id must be sequential (1-200)
6. delay values must follow timing pattern table
7. voice_id must match language column

# Validation Checklist
1. Row Count: Match the exact number of rows specified in the JSON for each segment.
2. Repetition Accuracy: Ensure 4 teaching repetitions and 3 practice repetitions per phrase.
3. Language Ratio: Adhere to the Danish/English ratio specified in the JSON.
4. Danish Voice Accuracy: Split rows for Danish words in mixed-language sentences and assign da_voice.

# Lesson Content

To be added here...