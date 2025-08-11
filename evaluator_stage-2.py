#!/usr/bin/env python3
"""
Graphical User Interface (GUI) Agent Evaluator App: Stage 2
"""

import tkinter as tk
from tkinter import ttk

import os
from constants import DIR_S1_OUTPUT
from constants import FORMAT_DATA
from read_errors_from_image import write_errors_summary
from utilities_io import load_json_file

class EvaluatorAppS2 :
    
    def __init__( self) -> None :
        
        self.root = tk.Tk()

        # Title and background color
        self.root.title("Agent Evaluator: Stage 2")
        self.root.configure( bg = 'black')

        # Grid spacing - rows 0 and 10 are padding, columns 0 and 8 are padding
        self.root.grid_rowconfigure(    0, minsize = 10)  # Top padding
        self.root.grid_rowconfigure(   10, minsize = 10)  # Bottom padding
        self.root.grid_columnconfigure( 0, minsize = 10)  # Left border padding
        self.root.grid_columnconfigure( 2, minsize = 10)  # Left middle padding
        self.root.grid_columnconfigure( 6, minsize = 10)  # Right middle padding
        self.root.grid_columnconfigure( 8, minsize = 10)  # Right border padding
        
        # Text Boxes: Parameters
        self.TEXT_WIDTH  = 48
        self.TEXT_HEIGHT = 32
        self.TEXT_BG_COLOR = 'white'
        self.TEXT_FG_COLOR = 'black'
        # Text Boxes: Objects
        self.textbox_a = tk.Text( self.root,
                                  width = self.TEXT_WIDTH,
                                  height = self.TEXT_HEIGHT,
                                  bg = self.TEXT_BG_COLOR,
                                  fg = self.TEXT_FG_COLOR,
                                  wrap = tk.WORD )
        self.textbox_b = tk.Text( self.root,
                                  width = self.TEXT_WIDTH,
                                  height = self.TEXT_HEIGHT,
                                  bg = self.TEXT_BG_COLOR,
                                  fg = self.TEXT_FG_COLOR,
                                  wrap = tk.WORD )
        # Text Boxes: Place on grid
        self.textbox_a.grid( row = 1, column = 1, rowspan = 9, columnspan = 1,
                             padx = 5, pady = 5, sticky = "nsew" )
        self.textbox_b.grid( row = 1, column = 7, rowspan = 9, columnspan = 1,
                             padx = 5, pady = 5, sticky = "nsew" )
        # Text Boxes: Print placeholder
        self.textbox_print( 'A', "TEXTBOX_A", clear = True)
        self.textbox_print( 'B', "TEXTBOX_B", clear = True)

        # Buttons: Definitions
        self.buttons = {}
        self.buttons['<DATA']  = { 'row':2, 'col':3, 'fun': self.data_load_prev  }
        self.buttons['DATA>']  = { 'row':2, 'col':5, 'fun': self.data_load_next  }
        self.buttons['<ERROR'] = { 'row':3, 'col':3, 'fun': lambda x : None }
        self.buttons['EVAL']   = { 'row':3, 'col':4, 'fun': lambda x : None }
        self.buttons['ERROR>'] = { 'row':3, 'col':5, 'fun': lambda x : None }
        self.buttons['M1']     = { 'row':4, 'col':4, 'fun': lambda x : None }
        self.buttons['M2']     = { 'row':5, 'col':4, 'fun': lambda x : None }
        self.buttons['M3']     = { 'row':6, 'col':4, 'fun': lambda x : None }
        self.buttons['M4']     = { 'row':7, 'col':4, 'fun': lambda x : None }
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
        
        # Key bindings: Arrows
        self.root.bind( "<Left>",  lambda e: self.data_load_prev())
        self.root.bind( "<Right>", lambda e: self.data_load_next())
        
        # Initialize list of data filenames
        self.data_filenames = []
        for filename in sorted(os.listdir(DIR_S1_OUTPUT)) :
            if filename.lower().endswith(FORMAT_DATA) :
                self.data_filenames.append(filename)
        # Number of data files
        self.data_num = len(self.data_filenames)

        # Initialize data current index
        self.data_curr_index = 0
        self.data_load()
        
        return
    
    def data_load(self) -> None :
        # Get data name, path, object and string
        self.data_name = self.data_filenames[self.data_curr_index]
        self.data_path = os.path.join( DIR_S1_OUTPUT, self.data_name)
        self.data_obj  = load_json_file(self.data_path)
        self.data_str  = write_errors_summary(self.data_obj)

        # Print image name to title and clear textbox
        self.root.title(f"Current data file: {self.data_name}")
        self.textbox_clear('A')
        self.textbox_clear('B')
        self.textbox_print( 'A', self.data_str)

        return
    
    def data_load_next(self) -> None :
        if 0 <= self.data_curr_index < self.data_num - 1 :
            self.data_curr_index += 1
            self.data_load()
        return
    
    def data_load_prev(self) -> None :
        if 1 <= self.data_curr_index < self.data_num :
            self.data_curr_index -= 1
            self.data_load()
        return
    
    def textbox_print( self, box : str, text : str, clear : bool = False) -> None :
        match box :
            case 'A' :
                if clear :
                    self.textbox_clear('A')
                self.textbox_a.insert( tk.END, text)
            case 'B' :
                if clear :
                    self.textbox_clear('B')
                self.textbox_b.insert( tk.END, text)
            case _ :
                raise ValueError( f"Invalid box: {box}")
        return
    
    def textbox_clear( self, box : str) -> None :
        match box :
            case 'A' :
                self.textbox_a.delete( 1.0, tk.END)
            case 'B' :
                self.textbox_b.delete( 1.0, tk.END)
            case _ :
                raise ValueError( f"Invalid box: {box}")
        return

if __name__ == "__main__":
    
    app = EvaluatorAppS2()
    app.root.mainloop()
