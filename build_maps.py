#!/usr/bin/env python3
"""
Traverse the pipeline error -> diagnosis -> component | problem
"""

import sys
from constants import DIR_DKNOWLEDGE_B
from constants import SUBSYSTEMS
from utilities_loading import load_domain_knowledge
from utilities_printing import print_recursively

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
    data = load_domain_knowledge( directory, system_type)
    
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
    
    dir_data = DIR_DKNOWLEDGE_B
    subsystems_msg = f"Available subsystems: {', '.join(SUBSYSTEMS)}"
    
    if len(sys.argv) != 3 :
        print(f"Usage: python build_maps.py <subsystem> <error>")
        print(subsystems_msg)
        sys.exit(1)
    
    input_subsystem = sys.argv[1]
    input_error     = sys.argv[2]
    
    if input_subsystem not in SUBSYSTEMS :
        print(f"❌ Error: Invalid subsystem '{input_subsystem}'")
        print(subsystems_msg)
        sys.exit(1)
    
    # Build the error map
    error_map = build_map( dir_data, input_subsystem)
    
    # Check if the error exists
    if input_error not in error_map :
        print(f"❌ Error: Error code '{input_error}' not found in subsystem '{input_subsystem}'")
        print(f"Available errors: {', '.join(sorted(error_map.keys()))}")
        sys.exit(1)
    
    # Print the result recursively
    print(f"Error: {input_error}")
    print(f"Subsystem: {input_subsystem}")
    print_recursively(error_map[input_error])
