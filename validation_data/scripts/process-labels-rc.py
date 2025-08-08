import os
import csv
import shutil
from PIL import Image
from tqdm import tqdm
import datetime

# Configuration
BASE_DIR = "/home/luis/DJI_AGRAS_LATINO"
RC_T40_T50_DIR = os.path.join(BASE_DIR, "rc", "t40_t50")
CSV_DIR = "/home/luis/kgraphs/labels"
INPUT_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50.csv")
LOG_FILE = os.path.join(CSV_DIR, "process-labels-rc.log")

# Output CSV files
SPRAY_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50_spray.csv")
PROP_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50_prop.csv")
FLIGHT_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50_flight.csv")
BATT_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50_batt.csv")
OTHER_CSV = os.path.join(CSV_DIR, "labels_DAL_rc_t40_t50_other.csv")

# Output directories
SPRAY_DIR = os.path.join(RC_T40_T50_DIR, "spray")
PROP_DIR = os.path.join(RC_T40_T50_DIR, "prop")
FLIGHT_DIR = os.path.join(RC_T40_T50_DIR, "flight")
BATT_DIR = os.path.join(RC_T40_T50_DIR, "batt")
OTHER_DIR = os.path.join(RC_T40_T50_DIR, "other")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [SPRAY_DIR, PROP_DIR, FLIGHT_DIR, BATT_DIR, OTHER_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def copy_image(filename, source_dir, dest_dir):
    """Copy image from source to destination directory"""
    source_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, filename)
    
    # Skip if source file doesn't exist
    if not os.path.exists(source_path):
        print(f"Warning: Source file not found: {source_path}")
        return False
    
    try:
        # Only copy if the file doesn't already exist in the destination
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
        return True
    except Exception as e:
        print(f"Error copying {filename}: {str(e)}")
        return False

def main():
    # Ensure directories exist
    ensure_directories()
    
    # Initialize lists for CSV files
    spray_labels = []
    prop_labels = []
    flight_labels = []
    batt_labels = []
    other_labels = []
    
    # First count total rows for progress bar
    total_rows = sum(1 for _ in open(INPUT_CSV))
    
    # Read and process the input CSV
    with open(INPUT_CSV, newline='') as f:
        reader = csv.reader(f)
        for row in tqdm(reader, total=total_rows, desc="Processing RC T40/T50 images"):
            if len(row) < 2:
                continue
                
            filename = row[0]
            labels = [label.strip() for label in row[2:] if label]
            
            # Check for specific labels
            has_spray = any('SPRAY' in label.upper() for label in labels)
            has_prop = any('PROP' in label.upper() for label in labels)
            has_flight = any('FLIGHT' in label.upper() for label in labels)
            has_batt = any('BATT' in label.upper() for label in labels)
            
            # If none of the specific labels are found, categorize as OTHER
            is_other = not (has_spray or has_prop or has_flight or has_batt)
            
            # Process image for each applicable category
            if has_spray:
                if copy_image(filename, RC_T40_T50_DIR, SPRAY_DIR):
                    spray_labels.append(row)
            
            if has_prop:
                if copy_image(filename, RC_T40_T50_DIR, PROP_DIR):
                    prop_labels.append(row)
            
            if has_flight:
                if copy_image(filename, RC_T40_T50_DIR, FLIGHT_DIR):
                    flight_labels.append(row)
            
            if has_batt:
                if copy_image(filename, RC_T40_T50_DIR, BATT_DIR):
                    batt_labels.append(row)
            
            if is_other:
                if copy_image(filename, RC_T40_T50_DIR, OTHER_DIR):
                    other_labels.append(row)
    
    # Write CSV files
    def write_csv(filename, rows):
        # Explicitly use Unix line endings
        with open(filename, 'w', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    write_csv(SPRAY_CSV, spray_labels)
    write_csv(PROP_CSV, prop_labels)
    write_csv(FLIGHT_CSV, flight_labels)
    write_csv(BATT_CSV, batt_labels)
    write_csv(OTHER_CSV, other_labels)
    
    # Print and log summary
    summary_lines = []
    summary_lines.append(f"Processing complete at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
    summary_lines.append(f"- SPRAY: {len(spray_labels)} files")
    summary_lines.append(f"- PROP: {len(prop_labels)} files")
    summary_lines.append(f"- FLIGHT: {len(flight_labels)} files")
    summary_lines.append(f"- BATT: {len(batt_labels)} files")
    summary_lines.append(f"- OTHER: {len(other_labels)} files")
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
