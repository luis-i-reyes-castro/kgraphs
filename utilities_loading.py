#!/usr/bin/env python3
"""
Functions for loading data after expansion
"""

from utilities_json import load_json_file
from utilities_json import load_json_files_starting_with

def load_domain_knowledge( directory : str, subsystem : str | None = None) -> dict :
    # Initialize results dict
    result = { 'errors'     : {},
               'diagnoses'  : {},
               'components' : {},
               'problems'   : {} }
    # If subsystem provided, load errors and diagnoses from that subsystem.
    if subsystem :
        result['errors']    = load_json_file(f'{directory}/errors_{subsystem}.json')
        result['diagnoses'] = load_json_file(f'{directory}/diagnoses_{subsystem}.json')
    # Else, load all errors and diagnoses.
    else :
        result['errors']    = load_json_files_starting_with( directory, 'errors_')
        result['diagnoses'] = load_json_files_starting_with( directory, 'diagnoses_')
    # Load all component and problem files
    result['components'] = load_json_files_starting_with( directory, 'components_')
    result['problems']   = load_json_files_starting_with( directory, 'problems_')
    # The grand finale
    return result
