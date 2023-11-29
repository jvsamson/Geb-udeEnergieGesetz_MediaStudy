import pandas as pd
import re
import os
from datetime import datetime

def clean_and_combine_subtitles(subtitle_file):
    # Determine program type based on file name
    program = 'tagesschau' if 'ts' in subtitle_file.lower() else 'tagesthemen' if 'tt' in subtitle_file.lower() else 'Unknown'

    # Extract and format date from file name
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', subtitle_file)
    if date_match:
        date_str = date_match.group(0)
        date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%y')
    else:
        date = 'Unknown Date'

    # Read the subtitle file
    df = pd.read_csv(subtitle_file, sep=';', header=0)

    # Filter out rows with metadata (identified by 'FABst' tags)
    df = df[~df['Subtitle'].str.contains('FABst')]

    # Initialize variables
    cleaned_subtitles = []
    current_subtitle = ''
    current_time_in = ''
    current_time_out = ''

    for index, row in df.iterrows():
        # Clean subtitle text
        cleaned_text = row['Subtitle'].replace('\n', ' ')  # Remove new lines
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
        cleaned_text = cleaned_text.strip()  # Remove leading and trailing spaces

        # Check if this is a continuation of the current subtitle
        if row['Timecode In'] == current_time_in:
            current_subtitle += ' ' + cleaned_text
            current_time_out = row['Timecode Out']
        else:
            # Add the previous subtitle to the list
            if current_subtitle:
                cleaned_subtitles.append([current_time_in, current_time_out, current_subtitle])

            # Start a new subtitle
            current_subtitle = cleaned_text
            current_time_in = row['Timecode In']
            current_time_out = row['Timecode Out']

    # Add the last subtitle to the list
    if current_subtitle:
        cleaned_subtitles.append([current_time_in, current_time_out, current_subtitle])

    # Create a new DataFrame
    cleaned_df = pd.DataFrame(cleaned_subtitles, columns=['Timecode In', 'Timecode Out', 'Subtitle'])

    # Correct special characters
    cleaned_df['Subtitle'] = cleaned_df['Subtitle'].apply(
        lambda x: x.replace('û', 'ss')
                .replace('Èu', 'ue')
                .replace('Èo', 'oe')
                .replace('Èa', 'ae')
    )

    # Add program and date columns
    cleaned_df['Program'] = program
    cleaned_df['Date'] = date
    
    return cleaned_df

# List to store each cleaned DataFrame
all_cleaned_data = []

# Directory to load CSV files from
load_directory = './data/cleaned/csv/'

# Loop through CSV files in the specified directory
for file_name in os.listdir(load_directory):
    if file_name.endswith('.csv'):
        full_path = os.path.join(load_directory, file_name)
        cleaned_df = clean_and_combine_subtitles(full_path)
        all_cleaned_data.append(cleaned_df)

# Concatenate all DataFrames into one
final_df = pd.concat(all_cleaned_data, ignore_index=True)

# Save the final DataFrame one level above the CSV folder
save_path = os.path.join(load_directory, '../all_cleaned_data.csv')
final_df.to_csv(save_path, index=False)
print(f"All data processed and saved to: {save_path}")
