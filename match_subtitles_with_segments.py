import pandas as pd
import os
import re

# Function to convert time string to seconds
def time_string_to_seconds(time_str):
    if ':' in time_str:  # Format "20:00:42.06" or "20:00:42,06"
        parts = time_str.split(':')
        h, m = parts[0], parts[1]
        s = parts[2].split('.')[0] if '.' in parts[2] else parts[2].split(',')[0]  # Handle both '.' and ',' as decimal separators
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:  # Format "2'20"""
        minutes, seconds = time_str.replace('"', '').split("'")
        return int(minutes) * 60 + int(seconds)

# Function to extract info from filename
def extract_info_from_filename(filename):
    match = re.search(r'subtitles_(\d{4}-\d{2}-\d{2})_(tt|ts)-(\d{4}).csv', filename)
    if match:
        date = match.group(1)
        programme = 'Tagesthemen' if match.group(2) == 'tt' else 'Tagesschau'
        start_time = match.group(3)[:2] + ':' + match.group(3)[2:] + ':00'
        return date, programme, start_time
    return None, None, None

# Function to match subtitles with segments
def match_subtitles_with_segments(segments_file, subtitles_folder, output_folder):
    segments_df = pd.read_csv(segments_file)

    for filename in os.listdir(subtitles_folder):
        if filename.endswith('.csv'):
            date, programme, start_time = extract_info_from_filename(filename)
            if date and programme:
                subtitles_df = pd.read_csv(os.path.join(subtitles_folder, filename))
                subtitles_df['Start Time Seconds'] = subtitles_df['Timecode In'].apply(lambda x: time_string_to_seconds(x))
                subtitles_df['End Time Seconds'] = subtitles_df['Timecode Out'].apply(lambda x: time_string_to_seconds(x))

                filtered_segments = segments_df[(segments_df['Programme'] == programme) & (segments_df['Date'] == date)].copy()
                filtered_segments['Start Time Seconds'] = filtered_segments['Start Time'].apply(lambda x: time_string_to_seconds(x))
                filtered_segments['End Time Seconds'] = filtered_segments.apply(lambda x: x['Start Time Seconds'] + time_string_to_seconds(x['Duration']), axis=1)

                # Joining segments and subtitles
                matched_segments = []
                for _, segment in filtered_segments.iterrows():
                    relevant_subtitles = subtitles_df[(subtitles_df['Start Time Seconds'] >= segment['Start Time Seconds']) & (subtitles_df['End Time Seconds'] <= segment['End Time Seconds'])]
                    full_text = ' '.join(relevant_subtitles['Subtitle'])
                    matched_segments.append({**segment.to_dict(), 'Combined Subtitles': full_text})

                matched_segments_df = pd.DataFrame(matched_segments)

                # Save the result
                output_file = os.path.join(output_folder, f"energie_gesetz_transkript_{date}.csv")
                matched_segments_df.to_csv(output_file, index=False)

# File paths
segments_file = 'combined_pdf_data.csv'
subtitles_folder = './data/cleaned/subtitles'
output_folder = './data/cleaned/transcripts'

# Process the matching
match_subtitles_with_segments(segments_file, subtitles_folder, output_folder)
