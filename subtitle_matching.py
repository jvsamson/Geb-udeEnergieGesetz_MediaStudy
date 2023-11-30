import pandas as pd

# Load the CSV file
csv_file_path = './data/cleaned/all_cleaned_data.csv'
df_csv = pd.read_csv(csv_file_path, sep=';')

# Convert 'Program' to lowercase for consistency in merging
df_csv['Program'] = df_csv['Program'].str.lower()

# Convert 'Date' in df_csv to datetime and then to 'dd.mm.yyyy' format
df_csv['Date'] = pd.to_datetime(df_csv['Date'], format='%d.%m.%y').dt.strftime('%d.%m.%Y')

# Load the Excel files for Tagesschau and Tagesthemen
tagesschau_file_path = './data/Tagesschau.xlsx'
tagesthemen_file_path = './data/Tagesthemen.xlsx'

# Selecting only necessary columns
columns_to_keep = ['Datum', 'Titel 1', 'Sendedauer Sendung', 'Uhrzeit']

df_tagesschau = pd.read_excel(tagesschau_file_path, header=1, usecols=columns_to_keep)
df_tagesthemen = pd.read_excel(tagesthemen_file_path, header=1, usecols=columns_to_keep)

# Process 'Titel 1' to extract program name and convert to lowercase
df_tagesschau['Processed Title'] = df_tagesschau['Titel 1'].str.extract(r'^(Tagesschau|Tagesthemen)')[0].str.lower()
df_tagesthemen['Processed Title'] = df_tagesthemen['Titel 1'].str.extract(r'^(Tagesschau|Tagesthemen)')[0].str.lower()

# Merge with Tagesschau data
merged_tagesschau = pd.merge(df_csv, df_tagesschau, left_on=['Program', 'Date'], right_on=['Processed Title', 'Datum'])

# Merge with Tagesthemen data
merged_tagesthemen = pd.merge(df_csv, df_tagesthemen, left_on=['Program', 'Date'], right_on=['Processed Title', 'Datum'])

# Combine both merged DataFrames
combined_df = pd.concat([merged_tagesschau, merged_tagesthemen], ignore_index=True)

# Save the combined DataFrame
combined_df.to_csv('all_cleaned_data_timed.csv')

# Print the combined DataFrame
print(combined_df)



import pandas as pd

# Adjusted frame rate (assumed frame rate; change if different)
frame_rate = 25

# Function to convert seconds since midnight to HH:MM:SS:FF format
def seconds_to_hhmmssff(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    frames = int((seconds - int(seconds)) * frame_rate)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}:{frames:02d}"

# Function to convert HH:MM:SS:FF to seconds
def hhmmssff_to_seconds(time_str):
    h, m, s, f = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s + f / frame_rate

# Assuming combined_df is already loaded and contains the 'Uhrzeit', 'Timecode In', 'Program' columns

# Convert 'Uhrzeit' to HH:MM:SS:FF format assuming 'Uhrzeit' is in seconds since midnight
combined_df['EP_Start'] = combined_df['Uhrzeit'].apply(seconds_to_hhmmssff)

# Detect new episodes
combined_df['new_episode'] = (
    (combined_df['Timecode In'] < combined_df['Timecode In'].shift(1, fill_value='00:00:00:00')) |
    (combined_df['Program'] != combined_df['Program'].shift(1)) |
    (combined_df['EP_Start'] != combined_df['EP_Start'].shift(1))
)

# Initialize episode counter
combined_df['episode_counter'] = combined_df['new_episode'].cumsum()

# Loop to calculate 'current_start' and 'current_end'
episode_starts = {}  # Dictionary to store the start times for each episode

for index, row in combined_df.iterrows():
    episode_num = row['episode_counter']
    
    if row['new_episode']:
        # New episode: set the start time and store it in the dictionary
        episode_starts[episode_num] = hhmmssff_to_seconds(row['EP_Start'])
        current_start_time = episode_starts[episode_num]
    else:
        # Same episode: retrieve the start time from the dictionary
        current_start_time = episode_starts[episode_num] + hhmmssff_to_seconds(row['Timecode In']) - hhmmssff_to_seconds(combined_df.iloc[0]['Timecode In'])

    # Calculate current_start and current_end relative to the episode start time
    combined_df.at[index, 'current_start'] = current_start_time
    combined_df.at[index, 'current_end'] = current_start_time + hhmmssff_to_seconds(row['Timecode Out']) - hhmmssff_to_seconds(row['Timecode In'])

# Convert 'current_start' and 'current_end' back to HH:MM:SS:FF format for display
combined_df['current_start'] = combined_df['current_start'].apply(seconds_to_hhmmssff)
combined_df['current_end'] = combined_df['current_end'].apply(seconds_to_hhmmssff)

# Display the DataFrame
print(combined_df[['Program', 'EP_Start', 'Timecode In', 'current_start', 'current_end', 'episode_counter']])