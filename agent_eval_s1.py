#!/usr/bin/env python3
"""
Graphical User Interface (GUI) Agent Evaluator App: Stage 1
"""

import tkinter as tk
from tkinter import ttk

import os
from abc_project_vars import DIR_S1_INPUT
from abc_project_vars import DIR_S1_OUTPUT
from abc_project_vars import FORMAT_IMG
from PIL import Image, ImageTk
from agent_decode_errors import read_errors
from agent_decode_errors import write_errors_summary
from utilities_io import ensure_dir
from utilities_io import exists_file
from utilities_io import load_json_file
from utilities_io import save_to_json_file

class EvaluatorAppS1 :
    
    def __init__( self) -> None :
        
        self.root = tk.Tk()

        # Title and background color
        self.root.title("Agent Evaluator: Stage 1")
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
        self.buttons['FIRST'] = { 'row':1, 'col':3, 'fun': self.image_load_first       }
        self.buttons['EVAL']  = { 'row':1, 'col':4, 'fun': self.image_evaluate_current }
        self.buttons['LAST']  = { 'row':1, 'col':5, 'fun': self.image_load_last        }
        self.buttons['PREV']  = { 'row':2, 'col':3, 'fun': self.image_load_prev        }
        self.buttons['SAVE']  = { 'row':2, 'col':4, 'fun': self.image_save_errors_json }
        self.buttons['NEXT']  = { 'row':2, 'col':5, 'fun': self.image_load_next        }
        self.buttons['LEFT']  = { 'row':3, 'col':3, 'fun': self.image_rotate_left  }
        self.buttons['DELETE']= { 'row':3, 'col':4, 'fun': self.image_delete_json  }
        self.buttons['RIGHT'] = { 'row':3, 'col':5, 'fun': self.image_rotate_right }
        # Buttons: Objects
        for key in self.buttons.keys() :
            # Initialize object and place it on the grid
            btn = ttk.Button( self.root,
                              text = key,
                              command = self.buttons[key]['fun'] )
            btn.grid( row    = self.buttons[key]['row'],
                      column = self.buttons[key]['col'] )
            # Store button reference for later state management
            self.buttons[key]['button'] = btn
        
        # Buttons: Colors
        self.BUTTON_BG_COLOR     = 'lightgray'
        self.BUTTON_SEL_BG_COLOR = [ ( 'selected', self.BUTTON_BG_COLOR) ]
        self.BUTTON_SEL_RELIEF   = [ ( 'selected', 'sunken') ]
        # Buttons: Default Style
        self.style = ttk.Style()
        self.style.configure( 'TButton', background = self.BUTTON_BG_COLOR)
        self.style.map(       'TButton', background = self.BUTTON_SEL_BG_COLOR,
                                         relief = self.BUTTON_SEL_RELIEF)
        # Buttons: Orange Style for Warnings
        self.style.configure( 'Orange.TButton', background = 'orange')
        
        # Key bindings: Arrows
        self.root.bind( "<Left>",  lambda e: self.image_load_prev())
        self.root.bind( "<Right>", lambda e: self.image_load_next())
        self.root.bind( "<Shift-Left>",  lambda e: self.image_rotate_left())
        self.root.bind( "<Shift-Right>", lambda e: self.image_rotate_right())
        # Key bindings: Numpad row upper
        self.root.bind( "<KP_7>", lambda e: self.image_load_first())
        self.root.bind( "<KP_8>", lambda e: self.image_evaluate_current())
        self.root.bind( "<KP_9>", lambda e: self.image_load_last())
        # Key bindings: Numpad row middle
        self.root.bind( "<KP_4>", lambda e: self.image_load_prev())
        self.root.bind( "<KP_5>", lambda e: self.image_save_errors_json())
        self.root.bind( "<KP_6>", lambda e: self.image_load_next())
        # Key bindings: Numpad row lower
        self.root.bind( "<KP_1>", lambda e: self.image_rotate_left())
        self.root.bind( "<KP_2>", lambda e: self.image_delete_json())
        self.root.bind( "<KP_3>", lambda e: self.image_rotate_right())
        
        # Initialize list of image filenames
        self.image_filenames = []
        for filename in sorted(os.listdir(DIR_S1_INPUT)) :
            if filename.lower().endswith(FORMAT_IMG) :
                self.image_filenames.append(filename)
        # Number of images
        self.image_num = len(self.image_filenames)
        
        # Load the first image
        self.image_load_first()

        # Ensure output directory exists
        ensure_dir(DIR_S1_OUTPUT)
        
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
        return
    
    def image_evaluate_current(self) -> None :
        # Clear text box and show status
        self.textbox_print( f"Calling LLM API. Please wait...\n", clear = True)
        self.root.update()
        
        # Call read_errors function
        self.image_errors_obj = None
        try:
            self.image_errors_obj = read_errors(self.image_current_path)
        except Exception as e:
            self.textbox_print( f"Exception thrown!\n", clear = True)
            self.textbox_print( f"Check console for exception info.\n")
            self.update_button_states()
            self.root.update()
            return
        
        self.textbox_clear()
        if self.image_errors_obj :
            self.image_errors_summary = write_errors_summary(self.image_errors_obj)
            self.textbox_print(f"Evaluation successful.\n")
            self.textbox_print(f"RESULTS:\n")
            self.textbox_print(self.image_errors_summary)
        else :
            self.textbox_print(f"Evaluation failure.\n")
            self.textbox_print(f"REASON: API returned None.\n")
        
        self.update_button_states()
        self.root.update()
        
        return
    
    def image_load(self) -> None :
        if self.image_filenames :
            # Get image name and path
            self.image_current_name = self.image_filenames[self.image_current_index]
            self.image_current_path = os.path.join( DIR_S1_INPUT, self.image_current_name)
            # Get corresponding image JSON file and path and check if it exists
            self.image_json_file   = self.image_current_name.replace( FORMAT_IMG, '.json')
            self.image_json_path   = os.path.join( DIR_S1_OUTPUT, self.image_json_file)
            self.image_json_exists = exists_file(self.image_json_path)
            
            # Load existing JSON file if it exists
            if self.image_json_exists :
                try :
                    self.image_errors_obj     = load_json_file(self.image_json_path)
                    self.image_errors_summary = write_errors_summary(self.image_errors_obj)
                except Exception as e :
                    self.image_errors_obj     = None
                    self.image_errors_summary = None
                    print(f"Error loading JSON file: {e}")
            else:
                # Clear textbox and reset evaluation state
                self.image_errors_obj     = None
                self.image_errors_summary = None
            
            # Print image name to title and clear textbox
            self.root.title(f"Current image: {self.image_current_name}")
            self.textbox_clear()
            
            # Display image and update button states and window
            self.image_display(self.image_current_path)
            
            # If we have existing results, display them in the textbox
            if self.image_errors_summary:
                self.textbox_print(f"EXISTING RESULTS:\n")
                self.textbox_print(self.image_errors_summary)
            
            # Update button states and window
            self.update_button_states()
            self.root.update()
        
        return
    
    def image_load_first(self) -> None :
        self.image_current_index = 0
        self.image_load()
        return
    
    def image_load_last(self) -> None :
        self.image_current_index = self.image_num - 1
        self.image_load()
        return
    
    def image_load_next(self) -> None :
        if 0 <= self.image_current_index < self.image_num - 1 :
            self.image_current_index += 1
            self.image_load()
        return

    def image_load_prev(self) -> None :
        if 1 <= self.image_current_index < self.image_num :
            self.image_current_index -= 1
            self.image_load()
        return
    
    def image_rotate( self, angle : int) -> None :
        self.image = self.image.rotate( angle, expand = True)
        self.image_display()
        return
    
    def image_rotate_left(self) -> None :
        self.image_rotate(+90)
        return
    
    def image_rotate_right(self) -> None :
        self.image_rotate(-90)
        return
    
    def image_save_errors_json(self) -> None :
        if self.image_errors_obj :
            save_to_json_file( self.image_errors_obj, self.image_json_path)
            self.textbox_print(f"RESULTS SAVED TO: {self.image_json_path}\n")
            self.image_json_exists = True
            self.update_button_states()
            self.root.update()
        return
    
    def image_delete_json(self) -> None :
        if self.image_json_exists and exists_file(self.image_json_path):
            try:
                os.remove(self.image_json_path)
                self.image_json_exists = False
                self.image_errors_obj = None
                self.image_errors_summary = None
                self.textbox_print(f"JSON file deleted: {self.image_json_path}\n", clear=True)
                self.update_button_states()
                self.root.update()
            except Exception as e:
                self.textbox_print(f"Error deleting JSON file: {e}\n", clear=True)
                self.root.update()
        return
    
    def textbox_print( self, text : str, clear : bool = False) -> None :
        if clear :
            self.textbox_clear()
        self.message_text.insert( tk.END, text)
        return
    
    def textbox_clear(self) -> None :
        self.message_text.delete( 1.0, tk.END)
        return
    
    def update_button_states(self) -> None :
        # Enable SAVE button only if we have evaluation results
        if hasattr( self, 'image_errors_obj') and self.image_errors_obj :
            self.buttons['SAVE']['button'].config( state = 'normal')
        else :
            self.buttons['SAVE']['button'].config( state = 'disabled')
        
        # Enable DELETE button only if JSON file exists
        if hasattr( self, 'image_json_exists') and self.image_json_exists :
            self.buttons['DELETE']['button'].config( state = 'normal')
        else :
            self.buttons['DELETE']['button'].config( state = 'disabled')
        
        # Set button background colors based on JSON file existence
        if hasattr( self, 'image_json_exists') and self.image_json_exists :
            # If JSON exists, set EVAL and SAVE buttons to orange background
            self.buttons['EVAL']['button'].configure( style = 'Orange.TButton')
            self.buttons['SAVE']['button'].configure( style = 'Orange.TButton')
        else :
            # If JSON doesn't exist, use default button style
            self.buttons['EVAL']['button'].configure( style = 'TButton')
            self.buttons['SAVE']['button'].configure( style = 'TButton')
        
        return

if __name__ == "__main__":
    
    app = EvaluatorAppS1()
    app.root.mainloop()
