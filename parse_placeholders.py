#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import data_structures as ds
import os
import shutil
import utilities as util
from parsing import parse_dict_of_dicts
from parsing import parse_list_of_pairs
from parsing import parse_diagnoses

if __name__ == "__main__" :
    
    placeholderDB = ds.load_placeholders()
    
    dir_input  = 'newlang/'
    dir_output = 'expansions/'
    batch_dod  = ( 'components_', 'errors_', 'problems_')
    batch_lop  = ( 'connections',)
    batch_dia  = ( 'diagnoses_',)
    batch_full = batch_dod + batch_lop + batch_dia
    exceptions = ( 'placeholders',)

    # List all files in the input directory
    for filename in os.listdir(dir_input) :
        path_input  = os.path.join(dir_input, filename)
        path_output = os.path.join(dir_output, filename)
        # Root out non-json files
        if not filename.endswith('.json') :
            continue
        # If file is not in batch and not in exceptions then copy
        if not filename.startswith(batch_full) :
            if not filename.startswith(exceptions) :
                shutil.copy (path_input, path_output)
                continue
            else :
                continue
        # Load the JSON file
        file_data   = util.load_json_file(path_input)
        parsed_data = None
        # Parse according to batch type
        if filename.startswith(batch_dod) :
            parsed_data = parse_dict_of_dicts( file_data, placeholderDB)
        elif filename.startswith(batch_lop) :
            parsed_data = parse_list_of_pairs( file_data, placeholderDB)
        elif filename.startswith(batch_dia) :
            parsed_data = parse_diagnoses( file_data, placeholderDB)
        else :
            raise ValueError( f'Unknown batch: {filename}')
        # Write the parsed data as JSON to the output directory
        util.save_json_file( path_output, parsed_data)
