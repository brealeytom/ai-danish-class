import pandas as pd
import os

# Define the file paths
input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'list_of_2000_phrases.csv')
output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'danish_phrases_clean.csv')

# Resolve the absolute paths
input_path = os.path.abspath(input_path)
output_path = os.path.abspath(output_path)

# Print the resolved paths for debugging
print(f"Input path: {input_path}")
print(f"Output path: {output_path}")

# Read the CSV file
df = pd.read_csv(input_path)

# Print initial statistics
print(f"Original row count: {len(df)}")

# First, remove exact duplicates
df_no_exact_dupes = df.drop_duplicates()
print(f"Rows after removing exact duplicates: {len(df_no_exact_dupes)}")
print(f"Removed {len(df) - len(df_no_exact_dupes)} exact duplicate rows")

# Create a language level priority mapping (lower is better)
level_priority = {
    'A1': 1,
    'A2': 2,
    'B1': 3,
    'B2': 4
}

# Add a numeric priority column for sorting
df_no_exact_dupes['level_priority'] = df_no_exact_dupes['languageLevel'].map(level_priority)

# Let's check if there are missing language levels that didn't get mapped
missing_levels = df_no_exact_dupes[df_no_exact_dupes['level_priority'].isna()]
if len(missing_levels) > 0:
    print(f"Warning: {len(missing_levels)} rows have language levels not in our mapping:")
    print(missing_levels['languageLevel'].unique())
    
    # Assign highest priority number to unknown levels
    df_no_exact_dupes['level_priority'] = df_no_exact_dupes['level_priority'].fillna(999)

# Sort by Danish phrase and then by level priority (ascending)
df_sorted = df_no_exact_dupes.sort_values(['danishPhrase', 'level_priority'])

# Keep the first occurrence of each Danish phrase (which will be the lowest level)
df_cleaned = df_sorted.drop_duplicates(subset=['danishPhrase'], keep='first')

# Now sort the cleaned dataframe by language level, situational context, and then alphabetically by Danish phrase
# First, create an order for the language levels
level_order = {
    'A1': 0,
    'A2': 1,
    'B1': 2,
    'B2': 3
}

# Add a sort key for the language level
df_cleaned['level_order'] = df_cleaned['languageLevel'].map(level_order)

# Sort by level, then by situational context, then alphabetically by Danish phrase
df_final = df_cleaned.sort_values(['level_order', 'situationalContext', 'danishPhrase'])

# Remove the temporary columns
df_final = df_final.drop(columns=['level_priority', 'level_order'])

# Verify that we have no more duplicates
remaining_dupes = df_final[df_final.duplicated(subset=['danishPhrase'], keep=False)]
if len(remaining_dupes) > 0:
    print(f"\nWarning: Still found {len(remaining_dupes)} rows with duplicate phrases after cleaning!")
else:
    print("\nSuccess: No duplicate phrases remaining")

# Print statistics after removing phrase duplicates
print(f"Rows after removing phrase duplicates: {len(df_final)}")
print(f"Removed {len(df_no_exact_dupes) - len(df_cleaned)} phrase duplicates")

# Save the cleaned CSV
df_final.to_csv(output_path, index=False, quoting=1)
print(f"Cleaned CSV saved as '{output_path}'")