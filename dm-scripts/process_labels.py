import os
import csv
import shutil
from PIL import Image
from tqdm import tqdm

# Configuration for DJI AGRAS LATINO
BASE_DIR = "/home/luis/DJI_AGRAS_LATINO"
SOURCE_DIR = os.path.join( BASE_DIR, "raw")
CSV_DIR = "/home/luis/kgraphs"
CSV_FILE = os.path.join( CSV_DIR, "labels_DAL.csv")
DRONE_CSV = os.path.join( CSV_DIR, "labels_DAL_drone.csv")
RC_CSV = os.path.join( CSV_DIR, "labels_DAL_rc.csv")
EMPTY_CSV = os.path.join( CSV_DIR, "labels_DAL_empty.csv")
ROTATE_IMAGES = False  # Set to True to enable image rotation

# Configuration for Latin Drone
# SOURCE_DIR = "/home/luis/Latin_Drone/raw"
# BASE_DIR = "/home/luis/Latin_Drone"
# CSV_FILE = "/home/luis/kgraphs/labels_LD.csv"
# EMPTY_CSV = os.path.join(BASE_DIR, "/home/luis/kgraphs/labels_LD_empty.csv")
# POSITIVE_CSV = os.path.join(BASE_DIR, "/home/luis/kgraphs/labels_LD_positive.csv")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for dir_name in ['drone', 'rc', 'empty']:
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
    
    try:
        if ROTATE_IMAGES and rotation:
            img = Image.open(source_path)
            img = img.rotate(int(rotation), expand=True)
            img.save(dest_path)
        else:
            shutil.copy2(source_path, dest_path)
        return True
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return False

def main():
    # Ensure directories exist
    ensure_directories()
    
    # Initialize lists for CSV files
    drone_labels = []
    rc_labels = []
    empty_labels = []
    
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
            
            # Check for DRONE and RC labels
            has_drone = any('DRONE' in label.strip() for label in row[2:] if label)
            has_rc = any('RC' in label.strip() for label in row[2:] if label)
            
            if has_drone:
                if process_image(filename, rotation, 'drone'):
                    drone_labels.append(row)
            elif has_rc:
                if process_image(filename, rotation, 'rc'):
                    rc_labels.append(row)
            else:
                if process_image(filename, rotation, 'empty'):
                    empty_labels.append(row)
    
    # Write CSV files
    def write_csv(filename, rows):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            if ROTATE_IMAGES:
                # Reset all rotation values to "0" if rotation is enabled
                writer.writerows([row[0:1] + ["0"] + row[2:] for row in rows])
            else:
                # Keep original rotation values if rotation is disabled
                writer.writerows(rows)
    
    write_csv(DRONE_CSV, drone_labels)
    write_csv(RC_CSV, rc_labels)
    write_csv(EMPTY_CSV, empty_labels)
    
    # Print summary
    print(f"Processing complete:")
    print(f"- {len(drone_labels)} files with DRONE labels copied to {os.path.join(BASE_DIR, 'drone')}")
    print(f"- {len(rc_labels)} files with RC labels copied to {os.path.join(BASE_DIR, 'rc')}")
    print(f"- {len(empty_labels)} files without labels copied to {os.path.join(BASE_DIR, 'empty')}")
    print(f"- Results written to {DRONE_CSV}, {RC_CSV}, and {EMPTY_CSV}")

if __name__ == "__main__":
    main()
