import os
from constants import DIR_IMGS
from constants import IMG_FORMATS
from PIL import Image, ImageTk

# GUI Modules
import tkinter as tk
from tkinter import ttk

# Image Labeling App
class ImageLabelingApp :
    
    # Make canvas size responsive to screen size
    def __init__( self) -> None :
        
        self.root = tk.Tk()
        
        # Get screen dimensions
        screen_width  = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive dimensions (use 80% of screen size)
        self.CANVAS_WIDTH  = int( screen_width  * 0.20 )
        self.CANVAS_HEIGHT = int( screen_height * 0.40 )
        self.CANVAS_RATIO = self.CANVAS_WIDTH / self.CANVAS_HEIGHT
        self.CANVAS_CTR_X = self.CANVAS_WIDTH  // 2
        self.CANVAS_CTR_Y = self.CANVAS_HEIGHT // 2
        self.CANVAS_BG_COLOR = 'black'

        # Make text box size responsive
        self.TEXT_WIDTH  = min( 20, screen_width  // 12)
        self.TEXT_HEIGHT = min( 30, screen_height // 40)
        self.TEXT_BG_COLOR = 'white'
        self.TEXT_FG_COLOR = 'black'

        self.BUTTON_BG_COLOR     = 'lightgray'
        self.BUTTON_SEL_BG_COLOR = [ ( 'selected', 'orange') ]
        self.BUTTON_SEL_RELIEF   = [ ( 'selected', 'sunken') ]
        
        # Title
        self.root.title("Evaluator for Agent Stage 1")
        # Background color
        self.root.configure( bg = self.CANVAS_BG_COLOR)
        
        # Make window size responsive and ensure it fits on screen
        # Calculate maximum window size that fits on screen
        max_window_width = int(screen_width * 0.95)
        max_window_height = int(screen_height * 0.95)
        
        # Calculate desired window size based on content
        desired_width = self.CANVAS_WIDTH + 400  # Canvas + controls + padding
        desired_height = self.CANVAS_HEIGHT + 200  # Canvas + text box + padding
        
        # Use the smaller of desired size or maximum screen size
        window_width = min(desired_width, max_window_width)
        window_height = min(desired_height, max_window_height)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set initial window size and position
        self.root.geometry(f"{int(window_width)}x{int(window_height)}+{x}+{y}")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Set minimum window size to prevent it from becoming too small
        min_width = self.CANVAS_WIDTH + 200
        min_height = self.CANVAS_HEIGHT + 100
        self.root.minsize(min_width, min_height)
        
        # Bind window resize event to handle canvas and text box resizing
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Ensure window is properly positioned and sized after initialization
        self.root.after(100, self.finalize_window_setup)
        
        # Configure grid weights for responsive layout
        # Rows: 0-10 (11 rows total)
        for i in range(11):
            self.root.grid_rowconfigure(i, weight=1)
        
        # Columns: 0-6 (7 columns total)
        for i in range(7):
            self.root.grid_columnconfigure(i, weight=1)

        # Canvas: Spans columns 0-1, rows 0-10
        self.canvas = tk.Canvas( self.root, width = self.CANVAS_WIDTH,
                                            height = self.CANVAS_HEIGHT,
                                            bg = self.CANVAS_BG_COLOR )
        self.canvas.grid( row = 0, column = 0, rowspan = 11, columnspan = 2, 
                          padx = 10, pady = 10, sticky="nsew")

        # Create a frame for controls on the right side (columns 3-5, rows 0-2)
        self.controls_frame = tk.Frame(self.root, bg=self.CANVAS_BG_COLOR)
        self.controls_frame.grid(row=0, column=3, rowspan=3, columnspan=3, 
                                padx=10, pady=10, sticky="nsew")
        
        # Configure controls frame grid (3x3 grid for buttons)
        for i in range(3):
            self.controls_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.controls_frame.grid_columnconfigure(i, weight=1)

        # Message Text Box: Below controls frame, columns 3-5, rows 4-10
        self.message_text = tk.Text( self.root,
                                     width = self.TEXT_WIDTH,
                                     height = self.TEXT_HEIGHT,
                                     bg = self.TEXT_BG_COLOR,
                                     fg = self.TEXT_FG_COLOR,
                                     wrap = tk.WORD )
        self.message_text.grid( row = 4, column = 3, rowspan = 7, columnspan = 3,
                                padx = 10, pady = 10, sticky = "nsew" )
        
        # Navigation and rotation buttons
        self.buttons = {}
        # Buttons: First and Last
        self.buttons['FIRST'] = { 'row':0, 'col':0, 'fun': self.image_load_first }
        self.buttons['LAST']  = { 'row':0, 'col':2, 'fun': self.image_load_last }
        # Buttons: Prev and Next
        self.buttons['PREV']  = { 'row':1, 'col':0, 'fun': self.image_load_prev }
        self.buttons['NEXT']  = { 'row':1, 'col':2, 'fun': self.image_load_next }
        # Buttons: Rotate Left and Right
        self.buttons['LEFT']  = { 'row':2, 'col':0, 'fun': self.image_rotate_left  }
        self.buttons['RIGHT'] = { 'row':2, 'col':2, 'fun': self.image_rotate_right }
        # Buttons: Eval and Save
        self.buttons['EVAL']  = { 'row':1, 'col':1, 'fun': lambda x : None }
        self.buttons['SAVE']  = { 'row':2, 'col':1, 'fun': lambda x : None }
        
        # Add buttons to controls frame
        for key in self.buttons.keys() :
            btn = ttk.Button( self.controls_frame,
                              text = key,
                              command = self.buttons[key]['fun'] )
            btn.grid( row    = self.buttons[key]['row'],
                      column = self.buttons[key]['col'],
                      padx = 5, pady = 5, sticky="nsew" )
        
        # Configure style for the buttons
        self.style = ttk.Style()
        self.style.configure( 'TButton',
                              background = self.BUTTON_BG_COLOR )
        self.style.map( 'TButton',
                        background = self.BUTTON_SEL_BG_COLOR,
                        relief = self.BUTTON_SEL_RELIEF )
        
        # Key bindings: Arrows
        self.root.bind( "<Left>",  lambda e: self.image_load_prev())
        self.root.bind( "<Right>", lambda e: self.image_load_next())
        self.root.bind( "<Shift-Left>",  lambda e: self.image_rotate_left())
        self.root.bind( "<Shift-Right>", lambda e: self.image_rotate_right())
        
        # Key bindings: Numpad row upper
        self.root.bind( "<KP_7>", lambda e: self.image_load_first())
        self.root.bind( "<KP_8>", lambda e: None)
        self.root.bind( "<KP_9>", lambda e: self.image_load_last())
        # Key bindings: Numpad row middle
        self.root.bind( "<KP_4>", lambda e: self.image_load_prev())
        self.root.bind( "<KP_5>", lambda e: None)
        self.root.bind( "<KP_6>", lambda e: self.image_load_next())
        # Key bindings: Numpad row lower
        self.root.bind( "<KP_1>", lambda e: self.image_rotate_left())
        self.root.bind( "<KP_2>", lambda e: None)
        self.root.bind( "<KP_3>", lambda e: self.image_rotate_right())
        
        # Initialize list of image filenames
        self.image_filenames = []
        for filename in sorted(os.listdir(DIR_IMGS)) :
            if filename.lower().endswith(IMG_FORMATS) :
                self.image_filenames.append(filename)
        # Number of images
        self.image_num = len(self.image_filenames)
        
        # Load the first image
        self.image_load_first()
        
        # Display placeholder text
        self.message_text.insert( tk.END, "HELLO WORLD!\n")
        self.message_text.insert( tk.END, "HELLO WORLD!\n")
        self.message_text.insert( tk.END, "HELLO WORLD!\n")
        
        return
    
    def image_display( self, image_path : str | None = None) -> None :
        # Initialize image object
        if image_path :
            self.image = Image.open(image_path)
        # Calculate resizing dimensions
        self.image_ratio  = self.image.width / self.image.height
        # Case 1: Image is wider relative to height
        if self.image_ratio > self.CANVAS_RATIO :
            new_width  = self.CANVAS_WIDTH
            new_height = int( self.CANVAS_WIDTH / self.image_ratio )
        # Case 2: Image is taller relative to width
        else :
            new_height = self.CANVAS_HEIGHT
            new_width  = int( self.CANVAS_HEIGHT * self.image_ratio )
        # Resize image maintaining aspect ratio
        self.image_resized = self.image.resize( ( new_width, new_height),
                                                Image.Resampling.LANCZOS )
        # Center the image on canvas
        self.image_tk_pi = ImageTk.PhotoImage(self.image_resized)
        self.canvas.delete("all")
        self.canvas.create_image( self.CANVAS_CTR_X,
                                  self.CANVAS_CTR_Y,
                                  image=self.image_tk_pi)
        # The grand finale
        self.root.update()
        return
    
    def image_get_current_name(self) -> str | None :
        if self.image_filenames:
            return self.image_filenames[self.current_index]
        return None
    
    def image_load(self) -> None :
        if self.image_filenames:
            img_path = os.path.join( DIR_IMGS, self.image_filenames[self.current_index])
            self.image_display(img_path)
            self.update_button_states()
        return
    
    def image_load_first(self) -> None :
        self.current_index = 0
        self.image_load()
        return
    
    def image_load_last(self) -> None :
        self.current_index = self.image_num - 1
        self.image_load()
        return
    
    def image_load_next(self) -> None:
        if 0 <= self.current_index < self.image_num - 1 :
            self.current_index += 1
            self.image_load()
        return

    def image_load_prev(self) -> None:
        if 1 <= self.current_index < self.image_num :
            self.current_index -= 1
            self.image_load()
        return
    
    def image_rotate( self, angle : int) -> None :
        self.image = self.image.rotate( angle, expand = True)
        self.image_display()
        self.save_rotation(angle)
        return
    
    def image_rotate_left(self) -> None :
        self.image_rotate(+90)
        return
    
    def image_rotate_right(self) -> None :
        self.image_rotate(-90)
        return

    def update_button_states(self):
        pass
    
    def update_label_buttons(self):
        pass

    def save_rotation(self, angle_change):
        pass    

    def on_window_resize(self, event):
        # This method is called when the window is resized.
        # It can be used to update the canvas or text box size if they are
        # directly affected by the window size.
        # For now, it's a placeholder.
        pass

    def finalize_window_setup(self):
        # This method is called after the window has been initialized and
        # its geometry has been set. It can be used to perform any
        # final adjustments or calculations that depend on the window size.
        # For example, if the canvas or text box need to be resized
        # based on the final window size.
        pass

if __name__ == "__main__":
    
    app = ImageLabelingApp()
    app.root.mainloop()
