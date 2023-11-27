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
        segment_text = ''
        in_segment = False

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')

                for line in lines:
                    if 'Sende-/Haupttitel' in line:
                        current_programme = re.search(r'Sende-/Haupttitel:?\s*(.+)', line).group(1).strip()
                        continue

                    if 'Beitragstitel' in line:
                        current_section_title = re.search(r'Beitragstitel:?\s*(.+)', line).group(1).strip()
                        continue

                    if 'Moderation' in line:
                        moderator_info = re.search(r'Moderation:?\s*(.+),\s*(.+)', line)
                        if moderator_info:
                            current_moderation_name = f"{moderator_info.group(2).strip()}, {moderator_info.group(1).strip()}"
                        continue

                    if any(keyword in line for keyword in ['Sachinhalt', 'Bildinhalte', 'O-Ton']):
                        current_content_type = line.split(':')[0].strip()
                        in_segment = True
                        segment_text = ''
                        continue

                    if in_segment and 'TC Sequenz:' in line:
                        if segment_text:  # if there is already text captured, save it before starting a new segment
                            data.append({
                                'Programme': current_programme,
                                'Section Title': current_section_title,
                                'Content Type': current_content_type,
                                'Speaker Name': current_moderation_name,
                                'Speaker Description': '',
                                'Segment Description': segment_text.strip(),
                                'Start Time': start_time,
                                'Duration': duration
                            })
                        tc_info = re.search(r'TC Sequenz: (\d{2}:\d{2}:\d{2}\.\d{2}) Dauer: (\d{1,2}\'\d{2}")', line)
                        start_time = tc_info.group(1) if tc_info else ''
                        duration = tc_info.group(2) if tc_info else ''
                        segment_text = ''

                    elif in_segment:
                        segment_text += line + ' '

                # For the last segment on the page
                if in_segment and segment_text:
                    data.append({
                        'Programme': current_programme,
                        'Section Title': current_section_title,
                        'Content Type': current_content_type,
                        'Speaker Name': current_moderation_name,
                        'Speaker Description': '',
                        'Segment Description': segment_text.strip(),
                        'Start Time': start_time,
                        'Duration': duration
                    })
                    segment_text = ''
                    in_segment = False

    df = pd.DataFrame(data)
    return df

# Example usage
tagesschau_path = './data/Gebäudeenergiegesetz_Tagesschau.pdf'
tagesschau_df = extract_data_from_pdf(tagesschau_path)
tagesschau_df.to_csv('tagesschau_extracted_data.csv', index=False)
