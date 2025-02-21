import os
import csv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox

# Configuration
IMAGE_DIR = "/home/luis/DJI_AGRAS_LATINO/raw/"
CSV_FILE = "/home/luis/kgraphs/labels.csv"

class ImageLabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

        # Load image list
        self.image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        self.current_index = 0

        # Configure grid spacing
        root.grid_rowconfigure(0, weight=1)  # Top spacing
        root.grid_rowconfigure(10, weight=1)  # Bottom spacing
        root.grid_columnconfigure(0, minsize=20)  # Left spacing
        root.grid_columnconfigure(2, minsize=20)  # Spacing between canvas and buttons
        root.grid_columnconfigure(4, minsize=20)  # Right spacing

        # UI Elements
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.grid(row=1, column=1, rowspan=9)  # Moved to column 1

        self.btn_prev = ttk.Button(root, text="PREV", command=self.previous_image)
        self.btn_prev.grid(row=1, column=3)  # Moved to column 3

        self.btn_next = ttk.Button(root, text="NEXT", command=self.next_image)
        self.btn_next.grid(row=2, column=3)  # Moved to column 3

        self.btn_rotate_left = ttk.Button(root, text="LEFT", command=self.rotate_left)
        self.btn_rotate_left.grid(row=3, column=3)  # Moved to column 3

        self.btn_rotate_right = ttk.Button(root, text="RIGHT", command=self.rotate_right)
        self.btn_rotate_right.grid(row=4, column=3)  # Moved to column 3

        self.btn_last = ttk.Button(root, text="LAST", command=self.load_last_index)
        self.btn_last.grid(row=5, column=3)  # Moved to column 3

        self.label_buttons = {}
        # Group A buttons (CR and DRONE)
        for i, label in enumerate(["CR", "DRONE"]):
            btn = tk.Button(root, text=label,
                          command=lambda l=label: self.label_image(l, "A"),
                          relief='raised',
                          bg='lightgray',
                          font=('TkDefaultFont', 9, 'bold'))
            btn.grid(row=6 + i, column=3)
            self.label_buttons[label] = btn

        # Group B buttons (T40, T30, T50)
        for i, label in enumerate(["T40", "T30", "T50"]):
            btn = tk.Button(root, text=label,
                          command=lambda l=label: self.label_image(l, "B"),
                          relief='raised',
                          bg='lightgray',
                          font=('TkDefaultFont', 9, 'bold'))
            btn.grid(row=8 + i, column=3)
            self.label_buttons[label] = btn

        # Key bindings
        self.root.bind("<Left>", lambda e: self.previous_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Shift-Left>", lambda e: self.rotate_left())
        self.root.bind("<Shift-Right>", lambda e: self.rotate_right())
        
        # Bind numpad keys
        self.root.bind("<KP_7>", lambda e: self.label_image("CR", "A"))
        self.root.bind("<KP_9>", lambda e: self.label_image("DRONE", "A"))
        self.root.bind("<KP_4>", lambda e: self.label_image("T40", "B"))
        self.root.bind("<KP_3>", lambda e: self.label_image("T30", "B"))
        self.root.bind("<KP_5>", lambda e: self.label_image("T50", "B"))

        self.load_last_index()
    
    def load_image(self):
        if not self.image_files:
            return
        img_path = os.path.join(IMAGE_DIR, self.image_files[self.current_index])
        self.image = Image.open(img_path)
        
        # Apply saved rotation
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
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
        self.canvas.create_image(x, y, image=self.tk_image)
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            # Check if both groups have labels
            img_name = self.image_files[self.current_index]
            has_group_a = False
            has_group_b = False
            
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row[0] == img_name:
                            has_group_a = bool(row[2]) if len(row) > 2 else False
                            has_group_b = bool(row[3]) if len(row) > 3 else False
                            break

            # Warn if only one group is labeled
            if (has_group_a and not has_group_b) or (not has_group_a and has_group_b):
                tk.messagebox.showwarning("Warning", "You have only selected a label from one group. It's recommended to select both a type (CR/DRONE) and a size (T30/T40/T50).")
            
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
    
    def label_image(self, label, group):
        img_name = self.image_files[self.current_index]
        rows = []
        current_rotation = 0
        current_group_a = ""
        current_group_b = ""
        
        # Read existing labels
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == img_name:
                        current_rotation = int(row[1]) if row[1] else 0
                        current_group_a = row[2] if len(row) > 2 else ""
                        current_group_b = row[3] if len(row) > 3 else ""
                    else:
                        rows.append(row)

        # Reset buttons in the corresponding group
        group_a_labels = ["CR", "DRONE"]
        group_b_labels = ["T40", "T30", "T50"]
        
        if group == "A":
            for btn_label in group_a_labels:
                self.label_buttons[btn_label].configure(bg='lightgray')
            if current_group_a == label:  # Toggle off
                current_group_a = ""
            else:  # Toggle on
                current_group_a = label
                self.label_buttons[label].configure(bg='green')
        else:  # group B
            for btn_label in group_b_labels:
                self.label_buttons[btn_label].configure(bg='lightgray')
            if current_group_b == label:  # Toggle off
                current_group_b = ""
            else:  # Toggle on
                current_group_b = label
                self.label_buttons[label].configure(bg='green')

        # Write back with new format: filename, rotation, group A, group B
        rows.append([img_name, str(current_rotation), current_group_a, current_group_b])
        
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    def load_last_index(self):
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
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
            btn.configure(bg='lightgray')
            
        # Check current image label
        img_name = self.image_files[self.current_index]
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == img_name:
                        # Check group A label
                        if len(row) > 2 and row[2] in self.label_buttons:
                            self.label_buttons[row[2]].configure(bg='green')
                        # Check group B label
                        if len(row) > 3 and row[3] in self.label_buttons:
                            self.label_buttons[row[3]].configure(bg='green')
                        break

    def save_rotation(self, angle_change):
        img_name = self.image_files[self.current_index]
        rows = []
        current_rotation = 0
        current_group_a = ""
        current_group_b = ""
        
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[0] == img_name:
                        try:
                            current_rotation = int(row[1]) if row[1] else 0
                        except ValueError:
                            current_rotation = 0
                        current_group_a = row[2] if len(row) > 2 else ""
                        current_group_b = row[3] if len(row) > 3 else ""
                    else:
                        rows.append(row)
        
        # Update rotation (normalize to 0-359)
        new_rotation = (current_rotation + angle_change) % 360
        rows.append([img_name, str(new_rotation), current_group_a, current_group_b])
        
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingApp(root)
    root.mainloop()
