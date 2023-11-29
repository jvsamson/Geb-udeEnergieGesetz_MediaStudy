import pandas as pd
import re

def clean_and_combine_subtitles(subtitle_file):
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
    cleaned_df['Subtitle'] = cleaned_df['Subtitle'].apply(lambda x: x.replace('È', 'E').replace('û', 'u'))

    return cleaned_df

# Example usage
subtitle_file = './data/cleaned/csv/Das_Erste-2023-03-15-tt-2215_edited.csv'
cleaned_df = clean_and_combine_subtitles(subtitle_file)

cleaned_df.to_csv('cleaned_subtitles.csv', index=False)

# Display the cleaned DataFrame
print(cleaned_df.head())
