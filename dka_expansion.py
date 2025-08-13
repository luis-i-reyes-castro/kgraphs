#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import os
import shutil
from abc_project_vars import DIR_DKNOWLEDGE_A
from abc_project_vars import DIR_DKNOWLEDGE_B
from dka_data_structures import load_placeholders
from dka_parsing import parse_dict_of_dicts
from dka_parsing import parse_list_of_pairs
from dka_parsing import parse_diagnoses
from utilities_io import ensure_dir
from utilities_io import load_json_file
from utilities_io import save_to_json_file
from utilities_printing import print_ind

if __name__ == "__main__" :
    
    dir_input  = DIR_DKNOWLEDGE_A
    dir_output = DIR_DKNOWLEDGE_B

    print_ind(f'Expanding domain knowledge from: {dir_input}')
    ensure_dir(dir_output)
    print_ind(f'Saving files to: {dir_output}')

    batch_dod  = ( 'components_', 'messages_', 'problems_')
    batch_lop  = ( 'connections',)
    batch_dia  = ( 'diagnoses_',)
    exceptions = ( 'placeholders',)

    # Load the placeholder database
    path_placeholders = os.path.join( dir_input, 'placeholders.json')
    placeholderDB     = load_placeholders(path_placeholders)
    # List all files in the input directory
    dir_input_filenames = os.listdir(dir_input)
    dir_input_filenames.sort()
    for filename in dir_input_filenames :
        path_input  = os.path.join( dir_input, filename)
        path_output = os.path.join( dir_output, filename)
        print_ind(f'Processing file: {path_input}')
        # Root out non-json files
        if not filename.endswith('.json') :
            print_ind( f'File is not JSON. Skipped.', 1)
            continue
        # If file is not in batch and not in exceptions then copy
        batch_full = batch_dod + batch_lop + batch_dia
        if not filename.startswith(batch_full) :
            if not filename.startswith(exceptions) :
                shutil.copy (path_input, path_output)
                print_ind( f'File is neither expandable nor in exceptions. Copied.', 1)
            else :
                print_ind( f'File is in exceptions. Skipped.', 1)
            continue
        # Load the JSON file
        file_data   = load_json_file(path_input)
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
        save_to_json_file( parsed_data, path_output)
        print_ind( f'File data expanded.', 1)
