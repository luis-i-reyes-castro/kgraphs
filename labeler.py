import os
import csv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Configuration
IMAGE_DIR = "/home/luis/DJI_AGRAS_LATINO/raw/"
CSV_FILE = "/home/luis/DJI_AGRAS_LATINO/labels.csv"

class ImageLabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

        # Load image list
        self.image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        self.current_index = 0

        # UI Elements
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.grid(row=0, column=0, rowspan=7)

        self.btn_prev = ttk.Button(root, text="Previous", command=self.previous_image)
        self.btn_prev.grid(row=0, column=1)

        self.btn_next = ttk.Button(root, text="Next", command=self.next_image)
        self.btn_next.grid(row=1, column=1)

        self.btn_rotate_left = ttk.Button(root, text="Rotate Left", command=self.rotate_left)
        self.btn_rotate_left.grid(row=2, column=1)

        self.btn_rotate_right = ttk.Button(root, text="Rotate Right", command=self.rotate_right)
        self.btn_rotate_right.grid(row=3, column=1)

        self.btn_last = ttk.Button(root, text="Last Processed", command=self.load_last_index)
        self.btn_last.grid(row=4, column=1)

        # Label buttons
        for i, label in enumerate(["CR", "T40", "T30", "T50"]):
            btn = ttk.Button(root, text=label, command=lambda l=label: self.label_image(l))
            btn.grid(row=5 + i, column=1)

        # Key bindings
        self.root.bind("<Left>", lambda e: self.previous_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Shift-Left>", lambda e: self.rotate_left())
        self.root.bind("<Shift-Right>", lambda e: self.rotate_right())
        

        # **Move this line here, after UI is initialized**
        self.load_last_index()
    
    def load_image(self):
        if not self.image_files:
            return
        img_path = os.path.join(IMAGE_DIR, self.image_files[self.current_index])
        self.image = Image.open(img_path)
        self.display_image()
    
    def display_image(self):
        img_resized = self.image.resize((800, 600), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.canvas.create_image(400, 300, image=self.tk_image)
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()
    
    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()
    
    def rotate_left(self):
        self.image = self.image.rotate(90, expand=True)
        self.display_image()
    
    def rotate_right(self):
        self.image = self.image.rotate(-90, expand=True)
        self.display_image()
    
    def label_image(self, label):
        img_name = self.image_files[self.current_index]
        rows = []
        
        # Read existing labels
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as f:
                reader = csv.reader(f)
                rows = [row for row in reader if row[0] != img_name]
        
        # Append new label
        rows.append([img_name, label])
        
        # Write back
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingApp(root)
    root.mainloop()
