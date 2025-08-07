#!/usr/bin/env python3
"""
Functions for loading expansions
"""

import glob
import utilities as util

def load_data_expanded( directory : str) -> dict :
    """
    Load all diagnoses, components, problems, and errors from the specified directory.
    
    Args:
        directory: The directory containing the expansion files
        
    Returns:
        A dictionary containing all loaded data with keys:
        - 'diagnoses': All diagnoses files combined
        - 'components': All components files combined  
        - 'problems': All problems files combined
        - 'errors': All errors files combined
    """
    result = {
        'errors' : {},
        'diagnoses' : {},
        'components' : {},
        'problems' : {}
    }
    
    # Load all errors files
    errors_files = glob.glob(f'{directory}/errors_*.json')
    for file_path in errors_files :
        try :
            file_errors = util.load_json_file(file_path)
            result['errors'].update(file_errors)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    
    # Load all diagnoses files
    diagnoses_files = glob.glob(f'{directory}/diagnoses_*.json')
    for file_path in diagnoses_files :
        try :
            file_diagnoses = util.load_json_file(file_path)
            result['diagnoses'].update(file_diagnoses)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    
    # Load all components files
    components_files = glob.glob(f'{directory}/components_*.json')
    for file_path in components_files :
        try :
            file_components = util.load_json_file(file_path)
            result['components'].update(file_components)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    
    # Load all problems files
    problems_files = glob.glob(f'{directory}/problems_*.json')
    for file_path in problems_files :
        try :
            file_problems = util.load_json_file(file_path)
            result['problems'].update(file_problems)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    
    return result
