import os
import csv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import argparse
import sys

# Replace the hardcoded configuration with command line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='Image Labeling Tool - Phase 2')
    parser.add_argument('-img', '--image_dir', required=True,
                      help='Directory containing the images to label')
    parser.add_argument('-csv', '--csv_file', required=True,
                      help='Path to the CSV file for storing labels (must exist)')
    return parser.parse_args()

def validate_csv_with_image_dir(csv_file, image_dir):
    """
    Validates that the CSV file contains only images that exist in the image directory.
    Returns a tuple (is_valid, missing_images) where missing_images is a list of images in the CSV
    that don't exist in the image directory.
    """
    if not os.path.exists(csv_file):
        return False, ["CSV file does not exist"]
    
    # Get list of images in the directory
    image_files = set([f for f in os.listdir(image_dir) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
    
    # Check images in CSV
    missing_images = []
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] not in image_files:
                missing_images.append(row[0])
    
    return len(missing_images) == 0, missing_images

def ensure_csv_format(csv_file):
    """
    Ensures the CSV file has consistent line endings and format.
    Removes duplicate entries and fixes any formatting issues.
    """
    if not os.path.exists(csv_file):
        return
    
    # Read all entries from CSV
    entries = {}
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # Use the filename as key to avoid duplicates
            filename = row[0]
            # Store the rest of the data
            rotation = row[1] if len(row) > 1 else "0"
            group_a = row[2] if len(row) > 2 else ""
            group_b = row[3] if len(row) > 3 else ""
            group_c = row[4] if len(row) > 4 else ""
            group_d = row[5] if len(row) > 5 else ""
            
            # Fix quoted comma-separated values in group_c
            if group_c and group_c.startswith('"') and group_c.endswith('"'):
                group_c = group_c[1:-1]  # Remove quotes
            
            entries[filename] = [rotation, group_a, group_b, group_c, group_d]
    
    # Write back with consistent format
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for filename, data in sorted(entries.items()):
            writer.writerow([filename] + data)
    
    return entries

def update_csv_entry(csv_file, img_name, new_data):
    """
    Updates a specific entry in the CSV file for the given image name.
    """
    updated = False
    rows = []

    # Read all entries from CSV
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == img_name:
                rows.append([img_name] + new_data)
                updated = True
            else:
                rows.append(row)

    # If the image was not found, add it
    if not updated:
        rows.append([img_name] + new_data)

    # Write back to CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(rows)

# Image Labeling App
class ImageLabelingApp:
    def __init__(self, root, image_dir, csv_file):
        self.root = root
        self.root.title("Image Labeling Tool - Phase 2")
        self.root.configure(bg='black')
        
        # Replace hardcoded paths with parameters
        self.image_dir = image_dir
        self.csv_file = csv_file
        
        # Update image loading to use the new path
        self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        self.current_index = 0

        # Configure grid spacing
        root.grid_rowconfigure(0, weight=10)  # Top spacing
        root.grid_rowconfigure(10, weight=10)  # Bottom spacing
        root.grid_columnconfigure(0, minsize=20)  # Left spacing
        root.grid_columnconfigure(2, minsize=20)  # Spacing between canvas and buttons
        root.grid_columnconfigure(6, minsize=20)  # Right spacing

        # UI Elements
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.grid(row=1, column=1, rowspan=9)

        # Navigation and rotation buttons
        self.btn_prev = ttk.Button(root, text="PREV", command=self.previous_image)
        self.btn_prev.grid(row=1, column=3)

        self.btn_next = ttk.Button(root, text="NEXT", command=self.next_image)
        self.btn_next.grid(row=1, column=4)

        self.btn_rotate_left = ttk.Button(root, text="LEFT", command=self.rotate_left)
        self.btn_rotate_left.grid(row=2, column=3)

        self.btn_rotate_right = ttk.Button(root, text="RIGHT", command=self.rotate_right)
        self.btn_rotate_right.grid(row=2, column=4)

        self.btn_first = ttk.Button(root, text="FIRST", command=self.load_first_index)
        self.btn_first.grid(row=3, column=3)

        self.btn_last = ttk.Button(root, text="LAST", command=self.load_last_index)
        self.btn_last.grid(row=3, column=4)

        self.label_buttons = {}
        # Updated button layout with new labels
        button_layout = [
            ("RC", 4, 3), ("DRONE", 4, 4), ("OTHER", 4, 5),      # row 4
            ("T40", 5, 3), ("T50", 5, 4), ("BATT", 5, 5),        # row 5
            ("SPRAY", 6, 3), ("PROP", 6, 4), ("FLIGHT", 6, 5),   # row 6
        ]
        
        # Configure style for the buttons
        self.style = ttk.Style()
        self.style.configure('TButton', background='lightgray')
        self.style.map('TButton',
                      background=[('selected', 'orange')],
                      relief=[('selected', 'sunken')])
        
        for label, row, col in button_layout:
            # Determine the group for each button
            if label in ["RC", "DRONE"]:
                group = "A"
            elif label in ["T40", "T50"]:
                group = "B"
            else:  # New labels: SPRAY, PROP, FLIGHT, BATT, OTHER
                group = "C"
                
            btn = ttk.Button(root, text=label,
                          command=lambda l=label, g=group: self.label_image(l, g),
                          style='TButton')
            btn.grid(row=row, column=col)
            self.label_buttons[label] = btn

        # Key bindings
        self.root.bind("<Left>", lambda e: self.previous_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Shift-Left>", lambda e: self.rotate_left())
        self.root.bind("<Shift-Right>", lambda e: self.rotate_right())
        
        # Bind numpad keys - updated for new labels
        self.root.bind("<KP_7>", lambda e: self.label_image("RC", "A"))
        self.root.bind("<KP_8>", lambda e: self.label_image("DRONE", "A"))
        self.root.bind("<KP_9>", lambda e: self.label_image("OTHER", "C"))
        self.root.bind("<KP_1>", lambda e: self.label_image("SPRAY", "C"))
        self.root.bind("<KP_2>", lambda e: self.label_image("PROP", "C"))
        self.root.bind("<KP_3>", lambda e: self.label_image("FLIGHT", "C"))
        self.root.bind("<KP_4>", lambda e: self.label_image("T40", "B"))
        self.root.bind("<KP_5>", lambda e: self.label_image("T50", "B"))
        self.root.bind("<KP_6>", lambda e: self.label_image("BATT", "C"))

        self.load_first_csv_image()
        
        # Only call it once at the end of initialization
        # self.setup_key_bindings()
    
    def load_image(self):
        if not self.image_files:
            return
        img_path = os.path.join(self.image_dir, self.image_files[self.current_index])
        self.image = Image.open(img_path)
        
        # Apply saved rotation
        if os.path.exists(self.csv_file):
            with open(self.csv_file, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == self.image_files[self.current_index]:
                        if len(row) > 1:  # If rotation data exists
                            try:
                                rotation = int(row[1])  # rotation is in column 1
                                if rotation != 0:
                                    self.image = self.image.rotate(rotation, expand=True)
                            except ValueError:
                                # If rotation can't be parsed, assume 0
                                pass
                        break
        
        self.display_image()
        self.update_button_states()
    
    def display_image(self):
        # Calculate aspect ratios
        canvas_ratio = 800 / 600
        img_ratio = self.image.width / self.image.height

        # Calculate new dimensions maintaining aspect ratio
        if img_ratio > canvas_ratio:
            # Image is wider relative to height
            new_width = 800
            new_height = int(800 / img_ratio)
        else:
            # Image is taller relative to width
            new_height = 600
            new_width = int(600 * img_ratio)

        # Resize image maintaining aspect ratio
        img_resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        # Center the image on canvas
        x = 400  # canvas center x
        y = 300  # canvas center y
        self.canvas.delete("all")  # Clear previous image
        self.canvas.create_image(x, y, image=self.tk_image)
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            # Check if both groups have labels
            img_name = self.image_files[self.current_index]
            has_group_a = False
            has_group_b = False
            
            # Ensure current image is in CSV before moving on
            self.ensure_image_in_csv(img_name)
            
            if os.path.exists(self.csv_file):
                with open(self.csv_file, newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row[0] == img_name:
                            has_group_a = bool(row[2]) if len(row) > 2 else False
                            has_group_b = bool(row[3]) if len(row) > 3 else False
                            break

            # Warn if only one group is labeled
            if (has_group_a and not has_group_b) or (not has_group_a and has_group_b):
                tk.messagebox.showwarning("Warning", "You have only selected a label from one group. It's recommended to select both a type (RC/DRONE) and a size (T40/T50).")
                return  # Stay on current image
            
            self.current_index += 1
            self.load_image()
    
    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()
    
    def rotate_left(self):
        self.image = self.image.rotate(90, expand=True)
        self.save_rotation(90)
        self.display_image()
    
    def rotate_right(self):
        self.image = self.image.rotate(-90, expand=True)
        self.save_rotation(-90)
        self.display_image()
    
    def update_csv(self, img_name, new_values):
        """Update the CSV file with new values for a given image."""
        updated = False
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)

            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                for row in rows:
                    if row and row[0] == img_name:
                        # Update the row with new values
                        row[1:] = new_values
                        updated = True
                    writer.writerow(row)

            if not updated:
                # If the image was not found, append it
                with open(self.csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([img_name] + new_values)

    def label_image(self, label, group):
        """Label the image with the given label and group."""
        print(f"Debug: label_image called with label={label}, group={group}")
        
        img_name = self.get_current_image_name()
        print(f"Debug: Current image name: {img_name}")
        
        try:
            # Read the entire file into memory
            with open(self.csv_file, 'r', newline='') as f:
                lines = f.readlines()
            
            # Find the line for this image
            found = False
            modified = False
            new_lines = []
            
            for line in lines:
                line = line.rstrip('\r\n')  # Remove trailing newlines
                parts = line.split(',')
                
                if parts and parts[0] == img_name:
                    found = True
                    # Get current values
                    rotation = parts[1] if len(parts) > 1 else "0"
                    group_a = parts[2] if len(parts) > 2 else ""
                    group_b = parts[3] if len(parts) > 3 else ""
                    
                    # Get group C labels (all elements after index 3)
                    group_c_labels = [p for p in parts[4:] if p.strip()]
                    
                    # Update based on the group
                    original_line = line
                    if group == "A":
                        # Toggle label for group A
                        if group_a == label:
                            group_a = ""  # Remove label if it's already set
                        else:
                            group_a = label  # Set new label
                        modified = True
                    elif group == "B":
                        # Toggle label for group B
                        if group_b == label:
                            group_b = ""  # Remove label if it's already set
                        else:
                            group_b = label  # Set new label
                        modified = True
                    elif group == "C" and group_a == "RC":
                        # Toggle label for group C
                        if label in group_c_labels:
                            group_c_labels.remove(label)  # Remove label if it exists
                        else:
                            group_c_labels.append(label)  # Add label if it doesn't exist
                        modified = True
                    
                    # Create new line only if modified
                    if modified:
                        new_line = f"{img_name},{rotation},{group_a},{group_b}"
                        if group_c_labels:
                            for c_label in group_c_labels:
                                if c_label.strip():
                                    new_line += f",{c_label}"
                        print(f"Debug: Original line: {original_line}")
                        print(f"Debug: New line: {new_line}")
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # If image not found, add a new line
            if not found:
                rotation = "0"
                group_a = label if group == "A" else "RC" if group == "C" else ""
                group_b = label if group == "B" else ""
                group_c = label if group == "C" else ""
                
                new_line = f"{img_name},{rotation},{group_a},{group_b}"
                if group_c:
                    new_line += f",{group_c}"
                
                new_lines.append(new_line)
                modified = True
            
            # Only write back if something changed
            if modified:
                with open(self.csv_file, 'w', newline='') as f:
                    for line in new_lines:
                        f.write(line + '\n')
                
                print(f"Debug: File updated")
                print(f"Labeled {img_name} with {label} in group {group}")
            else:
                print(f"Debug: No changes needed")
            
            # Update the UI to reflect the changes
            self.update_label_buttons()
        
        except Exception as e:
            print(f"Error in label_image: {e}")
            import traceback
            traceback.print_exc()
    
    def load_last_index(self):
        if os.path.exists(self.csv_file):
            with open(self.csv_file, newline='') as f:
                reader = list(csv.reader(f))
                if reader:
                    last_image = reader[-1][0]
                    if last_image in self.image_files:
                        self.current_index = self.image_files.index(last_image)
        self.load_image()
        self.update_button_states()
    
    def update_button_states(self):
        # Reset all buttons
        for btn in self.label_buttons.values():
            btn.state(['!selected'])
            
        # Check current image label
        img_name = self.image_files[self.current_index]
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == img_name:
                        # Check group A label
                        if len(row) > 2 and row[2] in self.label_buttons:
                            self.label_buttons[row[2]].state(['selected'])
                        
                        # Check group B label
                        if len(row) > 3 and row[3] in self.label_buttons:
                            self.label_buttons[row[3]].state(['selected'])
                        
                        # Check group C labels (may have multiple values)
                        if len(row) > 4 and row[4]:
                            group_c_labels = row[4].split(',')
                            for label in group_c_labels:
                                if label and label in self.label_buttons:
                                    self.label_buttons[label].state(['selected'])
                        
                        # Check group D label (for backward compatibility)
                        if len(row) > 5 and row[5] in self.label_buttons:
                            self.label_buttons[row[5]].state(['selected'])
                        break

    def save_rotation(self, angle_change):
        img_name = self.image_files[self.current_index]
        
        # Read all entries from CSV
        entries = {}
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    filename = row[0]
                    rotation = row[1] if len(row) > 1 else "0"
                    group_a = row[2] if len(row) > 2 else ""
                    group_b = row[3] if len(row) > 3 else ""
                    group_c = row[4] if len(row) > 4 else ""
                    group_d = row[5] if len(row) > 5 else ""
                    entries[filename] = [rotation, group_a, group_b, group_c, group_d]
        
        # Get current values for this image
        current_values = entries.get(img_name, ["0", "", "", "", ""])
        try:
            current_rotation = int(current_values[0])
        except ValueError:
            current_rotation = 0
        
        # Update rotation (normalize to 0-359)
        new_rotation = (current_rotation + angle_change) % 360
        
        # Update the rotation value
        current_values[0] = str(new_rotation)
        entries[img_name] = current_values
        
        # Write all entries back to CSV
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for filename, data in sorted(entries.items()):
                writer.writerow([filename] + data)

    def ensure_image_in_csv(self, img_name):
        """Ensures the current image is in the CSV file with at least rotation data"""
        # Read all entries from CSV
        entries = {}
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    filename = row[0]
                    rotation = row[1] if len(row) > 1 else "0"
                    group_a = row[2] if len(row) > 2 else ""
                    group_b = row[3] if len(row) > 3 else ""
                    group_c = row[4] if len(row) > 4 else ""
                    group_d = row[5] if len(row) > 5 else ""
                    entries[filename] = [rotation, group_a, group_b, group_c, group_d]
        
        # Add image if not found
        if img_name not in entries:
            entries[img_name] = ["0", "", "", "", ""]
            
            # Write all entries back to CSV
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                for filename, data in sorted(entries.items()):
                    writer.writerow([filename] + data)

    def load_first_index(self):
        """Load the first image in the directory"""
        if self.image_files:
            self.current_index = 0
            self.load_image()
            self.update_button_states()

    def load_first_csv_image(self):
        """Load the first image found in the CSV file"""
        if os.path.exists(self.csv_file):
            with open(self.csv_file, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] in self.image_files:
                        self.current_index = self.image_files.index(row[0])
                        break
        self.load_image()
        self.update_button_states()

    def get_current_csv_values(self, img_name):
        """Returns the current values for an image from the CSV file"""
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == img_name:
                        # Return rotation, group_a, group_b, group_c, group_d
                        return [
                            row[1] if len(row) > 1 else "0",    # rotation
                            row[2] if len(row) > 2 else "",     # group_a
                            row[3] if len(row) > 3 else "",     # group_b
                            row[4] if len(row) > 4 else "",     # group_c
                            row[5] if len(row) > 5 else ""      # group_d
                        ]
        # Return default values if image not found in CSV
        return ["0", "", "", "", ""]

    def get_current_image_name(self):
        """Returns the current image name"""
        if self.image_files:
            return self.image_files[self.current_index]
        return None

    def update_label_buttons(self):
        """Updates the button states based on the current image label"""
        # Reset all buttons
        for btn in self.label_buttons.values():
            btn.state(['!selected'])
            
        # Check current image label
        img_name = self.get_current_image_name()
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == img_name:
                        # Check group A label
                        if len(row) > 2 and row[2] in self.label_buttons:
                            self.label_buttons[row[2]].state(['selected'])
                        
                        # Check group B label
                        if len(row) > 3 and row[3] in self.label_buttons:
                            self.label_buttons[row[3]].state(['selected'])
                        
                        # Check group C labels (may have multiple values)
                        if len(row) > 4 and row[4]:
                            group_c_labels = row[4].split(',')
                            for label in group_c_labels:
                                if label and label in self.label_buttons:
                                    self.label_buttons[label].state(['selected'])
                        
                        # Check group D label (for backward compatibility)
                        if len(row) > 5 and row[5] in self.label_buttons:
                            self.label_buttons[row[5]].state(['selected'])
                        break

if __name__ == "__main__":
    args = parse_arguments()
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' does not exist. Please provide an existing CSV file.")
        sys.exit(1)
    
    # Fix CSV format before validation
    ensure_csv_format(args.csv_file)
    
    # Validate that CSV file matches images in directory
    is_valid, missing_images = validate_csv_with_image_dir(args.csv_file, args.image_dir)
    if not is_valid:
        print(f"Error: CSV file contains images that don't exist in the image directory:")
        for img in missing_images[:10]:  # Show first 10 missing images
            print(f"  - {img}")
        if len(missing_images) > 10:
            print(f"  ... and {len(missing_images) - 10} more.")
        print("Please ensure the CSV file matches the images in the directory.")
        sys.exit(1)
        
    root = tk.Tk()
    app = ImageLabelingApp(root, args.image_dir, args.csv_file)
    root.mainloop()
