import os
import shutil
import time
from pathlib import Path
from collections import deque
from tqdm import tqdm

# Constants
SOURCE_DIR = "/media/luis/FAA47057A47017F9/DJI_AGRAS_LATINO"
BASE_DIR = "/home/luis/DAL"
COPIED_FILE = os.path.join(SOURCE_DIR, "copied.txt")
WINDOW_SIZE = 20

def ensure_directories():
    """Create necessary directories if they don't exist."""
    for dir_name in [BASE_DIR, os.path.join(BASE_DIR, "JPG"), os.path.join(BASE_DIR, "PNG")]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

def get_copied_files():
    """Read the list of already copied files or create an empty set."""
    if os.path.exists(COPIED_FILE):
        with open(COPIED_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def copy_files():
    """Copy files and track progress."""
    # Get list of already copied files
    copied_files = get_copied_files()
    
    # Get all JPG and PNG files
    files_to_copy = []
    for file in sorted(os.listdir(SOURCE_DIR)):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and file not in copied_files:
            files_to_copy.append(file)
    
    if not files_to_copy:
        print("No new files to copy.")
        return
    
    # Initialize progress bar and timing variables
    pbar = tqdm(total=len(files_to_copy), desc="Copying files")
    times = deque(maxlen=WINDOW_SIZE)
    
    try:
        with open(COPIED_FILE, 'a') as copied_log:
            for file in files_to_copy:
                start_time = time.time()
                
                # Determine destination directory based on file extension
                ext = file.lower()
                if ext.endswith(('.jpg', '.jpeg')):
                    dest_dir = os.path.join(BASE_DIR, "JPG")
                else:
                    dest_dir = os.path.join(BASE_DIR, "PNG")
                
                # Copy file
                shutil.copy2(os.path.join(SOURCE_DIR, file), os.path.join(dest_dir, file))
                
                # Log copied file
                copied_log.write(f"{file}\n")
                copied_log.flush()
                
                # Update timing and progress
                elapsed = time.time() - start_time
                times.append(elapsed)
                avg_time = sum(times) / len(times)
                remaining = avg_time * (len(files_to_copy) - pbar.n - 1)
                
                # Update progress bar
                pbar.set_postfix({'ETA': f'{remaining:.1f}s'})
                pbar.update(1)
                
    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Progress has been saved.")
    finally:
        pbar.close()

def main():
    try:
        ensure_directories()
        copy_files()
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
