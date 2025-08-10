import os
from constants import DIR_IMGS
from constants import IMG_FORMATS
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk

class EvaluatorApp :
    """
    Graphical User Interface (GUI) Evaluator for Agent Stage 1.
    """
    
    def __init__( self) -> None :
        
        self.root = tk.Tk()

        # Title and background color
        self.root.title("Evaluator for Agent Stage 1")
        self.root.configure( bg = 'black')

        # Grid spacing
        self.root.grid_rowconfigure(  0, weight = 10)   # Top spacing
        self.root.grid_rowconfigure( 10, weight = 10)   # Bottom spacing
        self.root.grid_columnconfigure( 0, minsize=20)  # Left spacing
        self.root.grid_columnconfigure( 2, minsize=20)  # Spacing between canvas and buttons
        self.root.grid_columnconfigure( 6, minsize=20)  # Right spacing
        
        # Canvas: Parameters
        self.CANVAS_WIDTH  = 800
        self.CANVAS_HEIGHT = 600
        self.CANVAS_RATIO  = self.CANVAS_WIDTH / self.CANVAS_HEIGHT
        self.CANVAS_CTR_X  = self.CANVAS_WIDTH // 2
        self.CANVAS_CTR_Y  = self.CANVAS_HEIGHT // 2
        self.CANVAS_BG_COLOR = 'black'
        # Canvas: Object
        self.canvas = tk.Canvas( self.root, width = self.CANVAS_WIDTH,
                                            height = self.CANVAS_HEIGHT,
                                            bg = self.CANVAS_BG_COLOR )
        self.canvas.grid( row = 1, column = 1, rowspan = 9)

        # Text box: Parameters
        self.TEXT_WIDTH  = 48
        self.TEXT_HEIGHT = 24
        self.TEXT_BG_COLOR = 'white'
        self.TEXT_FG_COLOR = 'black'
        # Text Box: Object
        self.message_text = tk.Text( self.root,
                                     width = self.TEXT_WIDTH,
                                     height = self.TEXT_HEIGHT,
                                     bg = self.TEXT_BG_COLOR,
                                     fg = self.TEXT_FG_COLOR,
                                     wrap = tk.WORD )
        self.message_text.grid( row = 5, column = 3, rowspan = 5, columnspan = 3, 
                                padx = 5, pady = 5, sticky = "nsew" )

        # Buttons: Definitions
        self.buttons = {}
        self.buttons['FIRST'] = { 'row':1, 'col':3, 'fun': self.image_load_first }
        self.buttons['LAST']  = { 'row':1, 'col':5, 'fun': self.image_load_last }
        self.buttons['PREV']  = { 'row':2, 'col':3, 'fun': self.image_load_prev }
        self.buttons['NEXT']  = { 'row':2, 'col':5, 'fun': self.image_load_next }
        self.buttons['LEFT']  = { 'row':3, 'col':3, 'fun': self.image_rotate_left  }
        self.buttons['RIGHT'] = { 'row':3, 'col':5, 'fun': self.image_rotate_right }
        self.buttons['EVAL']  = { 'row':2, 'col':4, 'fun': lambda x : None }
        self.buttons['SAVE']  = { 'row':3, 'col':4, 'fun': lambda x : None }
        # Buttons: Colors
        self.BUTTON_BG_COLOR     = 'lightgray'
        self.BUTTON_SEL_BG_COLOR = [ ( 'selected', 'orange') ]
        self.BUTTON_SEL_RELIEF   = [ ( 'selected', 'sunken') ]
        # Buttons: Object
        for key in self.buttons.keys() :
            btn = ttk.Button( self.root,
                              text = key,
                              command = self.buttons[key]['fun'] )
            btn.grid( row    = self.buttons[key]['row'],
                      column = self.buttons[key]['col'] )
        # Buttons: Style
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

if __name__ == "__main__":
    
    app = EvaluatorApp()
    app.root.mainloop()
