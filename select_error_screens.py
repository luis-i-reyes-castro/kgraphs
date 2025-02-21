import os
from pathlib import Path
import pytesseract
from PIL import Image
import cv2
import numpy as np
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
import signal

# Constants
JPG_DIR = "/home/luis/DAL/JPG"
OUTPUT_DIR = "/home/luis/DAL/ERROR_SCREENS"
MIN_TEXT_LENGTH = 20  # Minimum characters to consider it a valid text screen

def ensure_output_directory():
    """Create output directory if it doesn't exist."""
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def rotate_image(image, angle):
    """Rotate PIL Image by given angle."""
    return image.rotate(angle, expand=True)

def preprocess_image(img_array):
    """Preprocess image for better OCR results."""
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary)
    
    return denoised

def extract_text(image_path, timeout=30):
    """
    Try to extract text from image in different orientations.
    Now with timeout protection.
    """
    def timeout_handler(signum, frame):
        raise TimeoutError("OCR processing took too long")
    
    # Open image with PIL
    image = Image.open(image_path)
    
    # Try different rotations
    rotations = [0, 90, 180, 270]
    best_text = ""
    best_rotation = 0
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        for angle in rotations:
            # Rotate image
            rotated = rotate_image(image, angle)
            
            # Convert PIL image to numpy array for OpenCV
            img_array = np.array(rotated)
            
            # Preprocess
            processed = preprocess_image(img_array)
            
            # Extract text
            text = pytesseract.image_to_string(processed, lang='eng')
            
            # Keep the rotation that yields the most text
            if len(text) > len(best_text):
                best_text = text
                best_rotation = angle
    
    except TimeoutError as e:
        print(f"\nTimeout while processing {os.path.basename(image_path)}")
        return "", 0
    finally:
        # Disable alarm
        signal.alarm(0)
    
    return best_text, best_rotation

def process_single_image(file, jpg_dir=JPG_DIR, output_dir=OUTPUT_DIR):
    """Process a single image and return its results."""
    image_path = os.path.join(jpg_dir, file)
    result = None
    
    try:
        print(f"\nProcessing: {file}")
        
        # Check image size before processing
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            print(f"Skipping large file ({file_size/1024/1024:.1f}MB): {file}")
            return file, None
            
        text, rotation = extract_text(image_path)
        
        if text:  # Only process if we got some text
            if len(text.strip()) >= MIN_TEXT_LENGTH:
                # Copy to output directory with rotation info in filename
                image = Image.open(image_path)
                if rotation != 0:
                    image = rotate_image(image, rotation)
                
                base_name, ext = os.path.splitext(file)
                new_name = f"{base_name}_rot{rotation}{ext}"
                output_path = os.path.join(output_dir, new_name)
                
                image.save(output_path)
                
                result = {
                    'file': file,
                    'rotation': rotation,
                    'text_length': len(text.strip()),
                    'sample_text': text.strip()[:100]
                }
    
    except Exception as e:
        print(f"\nError processing {file}: {str(e)}")
    
    return file, result

def process_images():
    """Process all JPG images and copy those with readable text."""
    # Get list of JPG files
    jpg_files = [f for f in os.listdir(JPG_DIR) if f.lower().endswith(('.jpg', '.jpeg'))]
    
    # Read already processed files
    processed_files = set()
    processed_file = os.path.join(OUTPUT_DIR, "copied.txt")
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            processed_files = set(line.strip() for line in f)
    
    # Filter out already processed files
    jpg_files = [f for f in jpg_files if f not in processed_files]
    
    if not jpg_files:
        print("No new files to process.")
        return []
    
    # Calculate number of processes to use (N-1 cores)
    num_processes = max(1, mp.cpu_count() - 1)
    print(f"Using {num_processes} processes")
    
    # Process files in parallel
    results = []
    try:
        with mp.Pool(num_processes) as pool:
            with open(processed_file, 'a') as f:
                # Create iterator for parallel processing with progress bar
                pbar = tqdm(total=len(jpg_files), desc="Processing images")
                
                # Process files in parallel
                for file, result in pool.imap_unordered(process_single_image, jpg_files):
                    # Log processed file
                    f.write(f"{file}\n")
                    f.flush()
                    
                    # Store result if valid
                    if result is not None:
                        results.append(result)
                    
                    pbar.update(1)
                
                pbar.close()
                
    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Progress has been saved.")
        pool.terminate()
        pool.join()
    
    return results

def main():
    try:
        # Ensure output directory exists
        ensure_output_directory()
        
        # Process images
        results = process_images()
        
        # Save results to a report file
        report_path = os.path.join(OUTPUT_DIR, "ocr_results.txt")
        with open(report_path, 'w') as f:
            f.write("OCR Processing Results\n")
            f.write("====================\n\n")
            for r in results:
                f.write(f"File: {r['file']}\n")
                f.write(f"Rotation applied: {r['rotation']}°\n")
                f.write(f"Text length: {r['text_length']}\n")
                f.write(f"Sample text: {r['sample_text']}\n")
                f.write("-" * 50 + "\n")
        
        print(f"\nProcessing complete! Found {len(results)} potential error screens.")
        print(f"Results saved to {report_path}")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
