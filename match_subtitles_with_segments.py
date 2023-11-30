import pandas as pd
import os
import re
from datetime import datetime, timedelta

def parse_filename(filename):
    match = re.search(r"subtitles_(\d{4}-\d{2}-\d{2})_(ts|tt)-(\d{4}).csv", filename)
    date, program = match.groups()[:2]
    return date, program

def convert_date_format(date_str):
    if isinstance(date_str, str):
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
    return None

def convert_to_datetime(date_str, time_str):
    if '.' in time_str:  # handle frames if present
        time_str = time_str.split('.')[0]
    time_parts = time_str.split(':')
    formatted_time_str = ':'.join(time_parts[:3])
    return datetime.strptime(f"{date_str} {formatted_time_str}", "%Y-%m-%d %H:%M:%S")

def duration_to_seconds(duration_str):
    minutes, seconds = re.match(r"(\d+)'(\d+)""", duration_str).groups()
    return int(minutes) * 60 + int(seconds)

def map_program_name(abbreviation):
    return {'tt': 'Tagesthemen', 'ts': 'Tagesschau'}.get(abbreviation, abbreviation)

def process_file(file, segments_df):
    date, program_abbr = parse_filename(file)
    program_full = map_program_name(program_abbr)
    subtitles_df = pd.read_csv(f'./data/cleaned/subtitles/{file}')

    subtitles_df['Timecode In'] = subtitles_df['Timecode In'].apply(lambda x: convert_to_datetime(date, x))
    subtitles_df['Timecode Out'] = subtitles_df['Timecode Out'].apply(lambda x: convert_to_datetime(date, x))

    for index, segment in segments_df.iterrows():
        if segment['Date'] == date and segment['Programme'] == program_full:
            start_time_str = segment['Start Time'] if isinstance(segment['Start Time'], str) else '00:00:00'
            start_time = convert_to_datetime(segment['Date'], start_time_str.split('.')[0])
            duration_sec = duration_to_seconds(segment['Duration'])
            end_time = start_time + timedelta(seconds=duration_sec)

            relevant_subtitles = subtitles_df[(subtitles_df['Timecode In'] >= start_time) & (subtitles_df['Timecode Out'] <= end_time)]
            combined_text = ' '.join(relevant_subtitles['Subtitle'].tolist())
            segments_df.at[index, 'Subtitles'] = combined_text

            # Debugging: Print segment info and whether subtitles were found
            print(f"Segment: {segment['Section Title']}, Time: {start_time_str} - {end_time}, Subtitles Found: {'Yes' if combined_text else 'No'}")

    return segments_df

def main():
    segments_df = pd.read_csv('combined_pdf_data.csv')
    segments_df['Date'] = segments_df['Date'].apply(convert_date_format)
    segments_df['Subtitles'] = ''  # Initialize the subtitles column

    for file in os.listdir('./data/cleaned/subtitles'):
        if file.endswith('.csv'):
            segments_df = process_file(file, segments_df)

    segments_df.to_csv('segments_transcript.csv', index=False)

if __name__ == "__main__":
    main()
