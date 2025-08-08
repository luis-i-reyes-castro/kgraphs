#!/usr/bin/env python3
"""
Traverse the pipeline error -> diagnosis -> component | problem
"""

import loaders
from utilities import print_recursively
import sys

def build_map( directory : str, system_type : str) -> dict :
    """
    Build a mapping from errors to their associated components and problems.
    
    Args:
        directory: The directory containing the expansion files
        system_type: The subsystem type (spraying, propulsion, flight)
        
    Returns:
        A dictionary mapping error codes to tuples of (components_list, problems_list)
    """
    # Load subsystem data
    data = loaders.load_data_expanded( directory, system_type)
    
    # Initialize result mapping
    error_maps = {}
    
    # For each error, look up its diagnoses and collect components and problems
    for error_code in data['errors'].keys() :
        components = []
        problems = []
        
        # Get the diagnoses for this error
        if error_code in data['diagnoses'] :
            causes_list = data['diagnoses'][error_code]
            
            # Process each cause in the diagnoses
            for cause in causes_list :
                if not isinstance(cause, dict) :
                    continue
                
                # Collect components
                if 'component' in cause :
                    component_name = cause['component']
                    if component_name not in components :
                        components.append(component_name)
                        continue
                
                # Collect problems (any key starting with 'problem_')
                problem_keys = \
                [ key for key in cause.keys() if str(key).startswith('problem_') ]
                for problem_key in problem_keys :
                    problem_name = cause[problem_key]
                    if problem_name not in problems :
                        problems.append(problem_name)
        
        # Store the mapping for this error
        error_maps[error_code] = (components, problems)
    
    return error_maps

if __name__ == "__main__" :
    
    dir_data = 'data_expanded/'
    available_systems = [ 'spraying', 'propulsion', 'flight' ]
    
    if len(sys.argv) != 3 :
        print(f"Usage: python build_maps.py <subsystem> <error>")
        print(f"Available subsystems: {', '.join(available_systems)}")
        sys.exit(1)
    
    subsystem = sys.argv[1]
    error_code = sys.argv[2]
    
    if subsystem not in available_systems :
        print(f"❌ Error: Invalid subsystem '{subsystem}'")
        print(f"Available subsystems: {', '.join(available_systems)}")
        sys.exit(1)
    
    # Build the error map
    error_map = build_map( dir_data, subsystem)
    
    # Check if the error exists
    if error_code not in error_map :
        print(f"❌ Error: Error code '{error_code}' not found in subsystem '{subsystem}'")
        print(f"Available errors: {', '.join(sorted(error_map.keys()))}")
        sys.exit(1)
    
    # Print the result recursively
    print(f"Error: {error_code}")
    print(f"Subsystem: {subsystem}")
    print_recursively(error_map[error_code])
