import pandas as pd
import re
import os

def clean_and_combine_subtitles(subtitle_file):
    # Read the subtitle file
    df = pd.read_csv(subtitle_file, sep=';', header=0)

    # Filter out rows with metadata (identified by 'FABst' tags)
    df = df[~df['Subtitle'].str.contains('FABst|\\* Gong \\*|Copyright Untertitel')]

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
    
    return cleaned_df

def process_all_subtitles(directory_path, output_directory):
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.csv'):
            # Extract date and time stamp from the file name
            match = re.search(r'(\d{4}-\d{2}-\d{2})-(tt|ts)-(\d{4})', file_name)
            if match:
                date = match.group(1)
                time_stamp = match.group(2) + '-' + match.group(3)
                new_file_name = f'subtitles_{date}_{time_stamp}.csv'

                # Full path of the file
                full_path = os.path.join(directory_path, file_name)

                # Process and save the cleaned subtitles
                cleaned_df = clean_and_combine_subtitles(full_path)
                cleaned_df.to_csv(os.path.join(output_directory, new_file_name), index=False)
                print(f'Processed {file_name} and saved as {new_file_name}')

# Example usage
directory_path = './data/cleaned/csv'
output_directory = './data/cleaned/subtitles'

# Process all subtitle files
process_all_subtitles(directory_path, output_directory)
