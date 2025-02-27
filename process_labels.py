import os
import csv
import shutil
from PIL import Image
from tqdm import tqdm

# Configuration
SOURCE_DIR = "/home/luis/DJI_AGRAS_LATINO/raw"
BASE_DIR = "/home/luis/DJI_AGRAS_LATINO"
CSV_FILE = "/home/luis/kgraphs/labels_DAL.csv"
EMPTY_CSV = os.path.join(BASE_DIR, "/home/luis/kgraphs/labels_DAL_empty.csv")
POSITIVE_CSV = os.path.join(BASE_DIR, "/home/luis/kgraphs/labels_DAL_positive.csv")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for dir_name in ['label', 'no_label']:
        path = os.path.join(BASE_DIR, dir_name)
        if not os.path.exists(path):
            os.makedirs(path)

def process_image(filename, rotation, destination):
    """Copy and rotate image if needed"""
    source_path = os.path.join(SOURCE_DIR, filename)
    dest_path = os.path.join(BASE_DIR, destination, filename)
    
    # Skip if source file doesn't exist
    if not os.path.exists(source_path):
        print(f"Warning: Source file not found: {source_path}")
        return False
    
    # Open, rotate if needed, and save
    try:
        img = Image.open(source_path)
        if rotation:
            img = img.rotate(int(rotation), expand=True)
        img.save(dest_path)
        return True
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return False

def main():
    # Ensure directories exist
    ensure_directories()
    
    # Initialize lists for CSV files
    empty_labels = []
    positive_labels = []
    
    # First count total rows for progress bar
    total_rows = sum(1 for _ in open(CSV_FILE))
    
    # Read and process the input CSV
    with open(CSV_FILE, newline='') as f:
        reader = csv.reader(f)
        for row in tqdm(reader, total=total_rows, desc="Processing images"):
            if len(row) < 2:
                continue
                
            filename = row[0]
            rotation = row[1] if row[1] else "0"
            
            # Check if there are any labels (group A, B, or C)
            has_labels = any(label.strip() for label in row[2:] if label)
            
            if has_labels:
                if process_image(filename, rotation, 'label'):
                    positive_labels.append(row)
            else:
                if process_image(filename, rotation, 'no_label'):
                    empty_labels.append([filename, rotation])
    
    # Write empty labels CSV
    with open(EMPTY_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(empty_labels)
    
    # Write positive labels CSV
    with open(POSITIVE_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(positive_labels)
    
    # Print summary
    print(f"Processing complete:")
    print(f"- {len(positive_labels)} files with labels copied to {os.path.join(BASE_DIR, 'label')}")
    print(f"- {len(empty_labels)} files without labels copied to {os.path.join(BASE_DIR, 'no_label')}")
    print(f"- Results written to {EMPTY_CSV} and {POSITIVE_CSV}")

if __name__ == "__main__":
    main()
