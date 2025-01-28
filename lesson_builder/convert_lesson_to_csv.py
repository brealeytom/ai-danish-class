
import json
import csv


# Function to convert JSON to CSV format
def convert_to_csv(lesson_json):
    lesson_id = 1
    lesson_name = "First Meetings"
    
    # Create the CSV output
    csv_output = []
    
    # Initialize order_id for tracking the sequence
    order_id = 1
    
    # Process each item in the JSON structure
    for item in lesson_json["lesson_section"]["content"]:
        content = item["content"]
        voice_id = item["voice_id"]
        delay = item.get("delay", 0)
        
        # Handle the repeat logic to generate multiple rows
        repeat = item.get("repeat", 1)
        
        for _ in range(repeat):
            row = {
                "lesson_id": lesson_id,
                "lesson_name": lesson_name,
                "order_id": order_id,
                "language": "en" if voice_id.startswith("english") else "da",
                "voice_id": voice_id,
                "text": content,
                "delay": delay
            }
            csv_output.append(row)
            order_id += 1
    
    # Write to CSV file
    with open('lesson_output.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["lesson_id", "lesson_name", "order_id", "language", "voice_id", "text", "delay"])
        writer.writeheader()
        writer.writerows(csv_output)

# Run the conversion function
convert_to_csv(lesson_json)