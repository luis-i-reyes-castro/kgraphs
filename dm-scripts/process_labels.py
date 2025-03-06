import os
import csv
import shutil
from PIL import Image
from tqdm import tqdm
import datetime

# Configuration for DJI AGRAS LATINO
BASE_DIR = "/home/luis/DJI_AGRAS_LATINO"
SOURCE_DIR = os.path.join( BASE_DIR, "raw")
CSV_DIR = "/home/luis/kgraphs/labels"
CSV_FILE = os.path.join(CSV_DIR, "labels_DAL.csv")
LOG_FILE = os.path.join(CSV_DIR, "process_labels.log")
DRONE_T40_T50_CSV = os.path.join(CSV_DIR, "labels_DAL_drone_t40_t50.csv")
DRONE_T20_T30_CSV = os.path.join(CSV_DIR, "labels_DAL_drone_t20_t30.csv")
DRONE_OTHER_CSV = os.path.join(CSV_DIR, "labels_DAL_drone_other.csv")
RC_T40_T50_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50.csv")
RC_T20_T30_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t20_t30.csv")
RC_OTHER_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_other.csv")
EMPTY_CSV = os.path.join(CSV_DIR, "labels_DAL_empty.csv")
ROTATE_IMAGES = False  # Set to True to enable image rotation

# Configuration for Latin Drone
# BASE_DIR = "/home/luis/Latin_Drone"
# SOURCE_DIR = os.path.join( BASE_DIR, "raw")
# CSV_DIR = "/home/luis/kgraphs/labels"
# CSV_FILE = os.path.join(CSV_DIR, "labels_LD.csv")
# LOG_FILE = os.path.join(CSV_DIR, "process_labels.log")
# DRONE_T40_T50_CSV = os.path.join(CSV_DIR, "labels_LD_drone_t40_t50.csv")
# DRONE_T20_T30_CSV = os.path.join(CSV_DIR, "labels_LD_drone_t20_t30.csv")
# DRONE_OTHER_CSV = os.path.join(CSV_DIR, "labels_LD_drone_other.csv")
# RC_T40_T50_CSV = os.path.join(CSV_DIR, "labels_LD_rc_t40_t50.csv")
# RC_T20_T30_CSV = os.path.join(CSV_DIR, "labels_LD_rc_t20_t30.csv")
# RC_OTHER_CSV = os.path.join(CSV_DIR, "labels_LD_rc_other.csv")
# EMPTY_CSV = os.path.join(CSV_DIR, "labels_LD_empty.csv")
# ROTATE_IMAGES = False  # Set to True to enable image rotation

def ensure_directories():
    """Create necessary directories if they don't exist"""
    # Main categories
    for main_dir in ['drone', 'rc', 'empty']:
        # For drone and rc, create model-specific subdirectories
        if main_dir in ['drone', 'rc']:
            for model_dir in ['t40_t50', 't20_t30', 'other']:
                path = os.path.join(BASE_DIR, main_dir, model_dir)
                if not os.path.exists(path):
                    os.makedirs(path)
        else:
            # Just create the empty directory
            path = os.path.join(BASE_DIR, main_dir)
            if not os.path.exists(path):
                os.makedirs(path)

def determine_model_category(labels):
    """Determine the model category based on labels"""
    # Check for T40 or T50
    if any('T40' in label or 'T50' in label for label in labels if label):
        return 't40_t50'
    # Check for T20 or T30
    elif any('T20' in label or 'T30' in label for label in labels if label):
        return 't20_t30'
    # Default to other
    else:
        return 'other'

def process_image(filename, rotation, main_category, model_category=None):
    """Copy and rotate image if needed"""
    source_path = os.path.join(SOURCE_DIR, filename)
    
    # For empty category, don't use model subcategory
    if main_category == 'empty':
        dest_path = os.path.join(BASE_DIR, main_category, filename)
    else:
        dest_path = os.path.join(BASE_DIR, main_category, model_category, filename)
    
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
    drone_t40_t50_labels = []
    drone_t20_t30_labels = []
    drone_other_labels = []
    rc_t40_t50_labels = []
    rc_t20_t30_labels = []
    rc_other_labels = []
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
            labels = [label.strip() for label in row[2:] if label]
            
            # Check for DRONE and RC labels
            has_drone = any('DRONE' in label for label in labels)
            has_rc = any('RC' in label for label in labels)
            
            if has_drone:
                model_category = determine_model_category(labels)
                if process_image(filename, rotation, 'drone', model_category):
                    if model_category == 't40_t50':
                        drone_t40_t50_labels.append(row)
                    elif model_category == 't20_t30':
                        drone_t20_t30_labels.append(row)
                    else:
                        drone_other_labels.append(row)
            elif has_rc:
                model_category = determine_model_category(labels)
                if process_image(filename, rotation, 'rc', model_category):
                    if model_category == 't40_t50':
                        rc_t40_t50_labels.append(row)
                    elif model_category == 't20_t30':
                        rc_t20_t30_labels.append(row)
                    else:
                        rc_other_labels.append(row)
            else:
                if process_image(filename, rotation, 'empty', None):
                    empty_labels.append(row)
    
    # Write CSV files
    def write_csv(filename, rows):
        # Explicitly use Unix line endings
        with open(filename, 'w', newline='\n') as f:
            writer = csv.writer(f)
            if ROTATE_IMAGES:
                # Reset all rotation values to "0" if rotation is enabled
                writer.writerows([row[0:1] + ["0"] + row[2:] for row in rows])
            else:
                # Keep original rotation values if rotation is disabled
                writer.writerows(rows)
    
    write_csv(DRONE_T40_T50_CSV, drone_t40_t50_labels)
    write_csv(DRONE_T20_T30_CSV, drone_t20_t30_labels)
    write_csv(DRONE_OTHER_CSV, drone_other_labels)
    write_csv(RC_T40_T50_CSV, rc_t40_t50_labels)
    write_csv(RC_T20_T30_CSV, rc_t20_t30_labels)
    write_csv(RC_OTHER_CSV, rc_other_labels)
    write_csv(EMPTY_CSV, empty_labels)
    
    # Print and log summary
    summary_lines = []
    summary_lines.append(f"Processing complete at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
    summary_lines.append(f"- DRONE categories:")
    summary_lines.append(f"  - T40/T50: {len(drone_t40_t50_labels)} files")
    summary_lines.append(f"  - T20/T30: {len(drone_t20_t30_labels)} files")
    summary_lines.append(f"  - Other: {len(drone_other_labels)} files")
    summary_lines.append(f"- RC categories:")
    summary_lines.append(f"  - T40/T50: {len(rc_t40_t50_labels)} files")
    summary_lines.append(f"  - T20/T30: {len(rc_t20_t30_labels)} files")
    summary_lines.append(f"  - Other: {len(rc_other_labels)} files")
    summary_lines.append(f"- Empty: {len(empty_labels)} files")
    summary_lines.append(f"Results written to CSV files in {CSV_DIR}")
    
    # Print to console
    for line in summary_lines:
        print(line)
    
    # Write to log file
    with open(LOG_FILE, 'a', newline='\n') as log:
        log.write("\n".join(summary_lines))
        log.write("\n\n")  # Add extra newlines for separation between runs

if __name__ == "__main__":
    main()
