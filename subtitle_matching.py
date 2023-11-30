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

# Adjusted frame rate
frame_rate = 25

# Function to convert HH:MM:SS:FF to seconds
def hhmmssff_to_seconds(time_str):
    h, m, s, f = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s + f / frame_rate

# Function to convert seconds back to HH:MM:SS:FF format
def seconds_to_hhmmssff(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    frames = int((seconds - int(seconds)) * frame_rate)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

# Assuming combined_df is already loaded and contains the 'Timecode In', 'Timecode Out' columns

# Sort by 'Timecode In' if it's not sorted already
combined_df.sort_values(by='Timecode In', inplace=True)

# Detecting new episodes
combined_df['new_episode'] = combined_df['Timecode In'] < combined_df['Timecode In'].shift(1, fill_value='00:00:00:00')

# Initialize episode counter
combined_df['episode_counter'] = combined_df['new_episode'].cumsum()

# Initialize 'current_start' and 'current_end'
combined_df['current_start'] = combined_df['Timecode In'].apply(hhmmssff_to_seconds)
combined_df['current_end'] = combined_df['Timecode Out'].apply(hhmmssff_to_seconds)

# Calculate 'current_start' and 'current_end' for each subtitle
for index, row in combined_df.iterrows():
    if row['new_episode']:
        # At the start of a new episode, set the 'current_start' to 'Timecode In'
        combined_df.at[index, 'current_start'] = hhmmssff_to_seconds(row['Timecode In'])
    else:
        # Continue from the last 'current_end'
        if index > 0:
            combined_df.at[index, 'current_start'] = combined_df.at[index - 1, 'current_end'] + hhmmssff_to_seconds(row['Timecode In'])
    
    # Set the 'current_end' based on 'current_start' plus 'Timecode Out'
    combined_df.at[index, 'current_end'] = combined_df.at[index, 'current_start'] + hhmmssff_to_seconds(row['Timecode Out'])

# Convert 'current_start' and 'current_end' back to HH:MM:SS:FF format
combined_df['current_start'] = combined_df['current_start'].apply(seconds_to_hhmmssff)
combined_df['current_end'] = combined_df['current_end'].apply(seconds_to_hhmmssff)

# Display the DataFrame
print(combined_df[['Timecode In', 'Timecode Out', 'current_start', 'current_end', 'episode_counter']])
