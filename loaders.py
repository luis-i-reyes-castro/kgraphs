#!/usr/bin/env python3
"""
Functions for loading data after expansion
"""

import glob
import utilities as util

def load_files_starting_with( directory : str, prefix : str) -> dict :
    result = {}
    files  = glob.glob(f'{directory}/{prefix}*.json')
    for file_path in files :
        try :
            file_contents = util.load_json_file(file_path)
            result.update(file_contents)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    return result

def load_data_expanded( directory : str, subsystem : str | None = None) -> dict :
    # Initialize results dict
    result = { 'errors'     : {},
               'diagnoses'  : {},
               'components' : {},
               'problems'   : {} }
    # If subsystem provided, load errors and diagnoses from that subsystem.
    # Else, load all errors and diagnoses.
    if subsystem :
        result['errors']    = util.load_json_file(f'{directory}/errors_{subsystem}.json')
        result['diagnoses'] = util.load_json_file(f'{directory}/diagnoses_{subsystem}.json')
    else :
        result['errors']    = load_files_starting_with( directory, 'errors_')
        result['diagnoses'] = load_files_starting_with( directory, 'diagnoses_')
    # Load all component and problem files
    result['components'] = load_files_starting_with( directory, 'components_')
    result['problems']   = load_files_starting_with( directory, 'problems_')
    # The grand finale
    return result
