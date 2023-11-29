import pdfplumber
import pandas as pd
import re

def extract_data_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        current_programme = ''
        current_section_title = ''
        current_content_type = ''
        current_moderation_name = ''
        current_date = ''

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')

                for i, line in enumerate(lines):
                    # Extract date information
                    if 'ESD' in line:
                        date_match = re.search(r'ESD\s+(\d{2}\.\d{2}\.\d{4})', line)
                        if date_match:
                            current_date = date_match.group(1).strip()

                    # Extract programme and section title
                    if 'Sende-/Haupttitel' in line:
                        current_programme = re.search(r'Sende-/Haupttitel:?\s*(.+)', line).group(1).strip()
                    elif 'Beitragstitel' in line:
                        current_section_title = re.search(r'Beitragstitel:?\s*(.+)', line).group(1).strip()

                    # Handle Moderation
                    elif 'Moderation' in line:
                        moderator_info = re.search(r'Moderation:?\s*(.+),\s*(.+)', line)
                        if moderator_info:
                            current_moderation_name = f"{moderator_info.group(2).strip()} {moderator_info.group(1).strip()}"

                    # Process Bildinhalt, Sachinhalt, or O-Ton sections
                    elif any(keyword in line for keyword in ['Bildinhalt', 'Sachinhalt', 'O-Ton']):
                        current_content_type = line.strip()

                        # Parse following lines until the next section or end of page
                        j = i + 1
                        while j < len(lines) and not re.match(r'^(Bildinhalt|Sachinhalt|O-Ton|[0-9]{2}\.[0-9]{2}\.[0-9]{4})', lines[j]):
                            segment_line = lines[j]
                            # Skip specific lines and the following empty line and section marker
                            if 'seite' in segment_line.lower() or 'copyright' in segment_line.lower():
                                j += 1  # Skip this line
                                if j < len(lines) and lines[j].strip() == '':
                                    j += 1  # Skip the following empty line
                                    if j < len(lines) and lines[j] in ['O-Ton', 'Bildinhalt', 'Sachinhalt']:
                                        j += 1  # Skip the next section marker line
                                continue
                            if re.match(r'^\d+ (TC Sequenz:|Start-TC Beitrag:)', segment_line):
                                tc_info = re.search(r'(TC Sequenz:|Start-TC Beitrag:) (\d{2}:\d{2}:\d{2}\.\d{2}) Dauer: (\d{1,2}\'\d{2}")', segment_line)
                                start_time = tc_info.group(2) if tc_info else ''
                                duration = tc_info.group(3) if tc_info else ''
                                segment_text = ''
                                speaker_name = current_moderation_name
                                speaker_description = 'Moderation'

                                if current_content_type == 'O-Ton':
                                    # Special handling for O-Ton
                                    if j + 1 < len(lines):
                                        o_ton_line = lines[j + 1]
                                        if 'Aufsager' in o_ton_line:
                                            segment_text = 'Aufsager'
                                            speaker_name = o_ton_line.split(' ', 1)[1].strip()
                                            speaker_description = 'Korrespondent'
                                        else:
                                            # Handling the speaker name and description
                                            if ',' in o_ton_line:
                                                speaker_info = o_ton_line.split(',', 1)
                                                speaker_name = speaker_info[0].strip()
                                                speaker_description = speaker_info[1].split('(')[0].strip()
                                            else:
                                                speaker_name = o_ton_line.split('(')[0].strip()
                                                speaker_description = ''

                                            # Extracting the segment description
                                            segment_text = ''
                                            bracket_count = 0
                                            k = j + 1
                                            while k < len(lines):
                                                for char in lines[k]:
                                                    if char == '(':
                                                        bracket_count += 1
                                                    elif char == ')' and bracket_count > 0:
                                                        bracket_count -= 1
                                                        if bracket_count == 0:
                                                            segment_text += char
                                                            break
                                                    if bracket_count > 0:
                                                        segment_text += char
                                                if bracket_count == 0:
                                                    break
                                                k += 1
                                else:
                                    # Handling for Bildinhalt and Sachinhalt
                                    k = j + 1
                                    while k < len(lines) and not re.match(r'^\d+ (TC Sequenz:|Start-TC Beitrag:)', lines[k]):
                                        segment_text += lines[k] + ' '
                                        k += 1

                                data.append({
                                    'Programme': current_programme,
                                    'Section Title': current_section_title,
                                    'Content Type': current_content_type,
                                    'Speaker Name': speaker_name.strip(),
                                    'Speaker Description': speaker_description.strip(),
                                    'Segment Description': segment_text.strip(),
                                    'Date': current_date,
                                    'Start Time': start_time,
                                    'Duration': duration
                                })

                            j += 1

    return pd.DataFrame(data)

# Tagesschau data extraction
tagesschau_path = './data/Gebäudeenergiegesetz_Tagesschau.pdf'
tagesschau_df = extract_data_from_pdf(tagesschau_path)
tagesschau_df.to_csv('tagesschau_extracted_data.csv', index=False)

# Tagessthemen data extraction
tagesthemen_path = './data/Gebäudeenergiegesetz_Tagesthemen.pdf'
tagesthemen_df = extract_data_from_pdf(tagesthemen_path)
tagesthemen_df.to_csv('tagesthemen_extracted_data.csv', index=False)
