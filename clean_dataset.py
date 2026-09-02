import csv
import sys

input_file = '/tmp/songs_with_attributes_and_lyrics.csv'
output_file = 'data/raw/dataset_new.csv'

csv.field_size_limit(sys.maxsize)

with open(input_file, 'r', encoding='utf-8') as f_in, \
     open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    
    header = next(reader)
    # Find lyrics index
    lyrics_idx = header.index("lyrics") if "lyrics" in header else -1
    
    if lyrics_idx != -1:
        new_header = header[:lyrics_idx] + header[lyrics_idx+1:]
    else:
        new_header = header
    
    writer.writerow(new_header)
    
    count = 0
    for row in reader:
        if lyrics_idx != -1 and len(row) > lyrics_idx:
            new_row = row[:lyrics_idx] + row[lyrics_idx+1:]
        else:
            new_row = row
        writer.writerow(new_row)
        count += 1
        if count % 100000 == 0:
            print(f"Processed {count} rows...")

print(f"Done! Total rows: {count}")
