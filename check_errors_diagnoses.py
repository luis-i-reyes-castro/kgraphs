#!/usr/bin/env python3
"""
Check error mappings for consistency
"""

import sys
import os
from constants import DIR_DKNOWLEDGE_B
from constants import SUBSYSTEMS
from utilities_loading import load_domain_knowledge

def has_valid_words( cause : dict, valid_words : list[str]) -> bool :
    for word in valid_words:
        if any( str(key).startswith(word) for key in cause.keys() ) :
            return True
    return False

def has_valid_cause_keys( cause : dict) -> bool :
    valid_words = [ 'component', 'problem']
    cond_1 = has_valid_words( cause, valid_words)
    valid_words = [ 'probability', 'frequency' ]
    cond_2 = has_valid_words( cause, valid_words)
    return cond_1 and cond_2

def check_error_mappings( directory : str, system_type : str) -> bool :
    """
    Check that all errors are mapped exactly once with valid causes.
    """
    
    # Load all data using the new loader function
    data = load_domain_knowledge(directory)
    
    # Get all error codes from errors data
    all_error_codes = set(data['errors'].keys())

    # Create sets to track various conditions
    found_errors = set()
    errors_without_causes = set()
    errors_with_invalid_causes = set()

    # Go through each error in error_causes
    for error_code, causes_list in data['diagnoses'].items() :
        found_errors.add(error_code)
        
        # Check if the error has causes
        if not causes_list :
            errors_without_causes.add(error_code)
            continue
            
        # Check if each cause has the required keys
        for i, cause in enumerate(causes_list) :
            if not isinstance( cause, dict) :
                errors_with_invalid_causes.add(error_code)
                break
            if not has_valid_cause_keys(cause) :
                errors_with_invalid_causes.add(error_code)
                break

    # Find errors that are in errors file but not in causes file
    missing_errors = all_error_codes - found_errors

    # Find errors that are in causes file but not in errors file
    unknown_errors = found_errors - all_error_codes

    # Print results
    if not (missing_errors or unknown_errors or errors_without_causes or errors_with_invalid_causes) :
        print("✅ All errors are properly mapped exactly once with valid causes!")
        return True

    if missing_errors :
        print(f"\n❌ Errors present in errors files but missing from diagnoses files:")
        for error in sorted(missing_errors) :
            print(f"  - {error}")

    if unknown_errors :
        print(f"\n❌ Errors present in diagnoses files but not defined in errors files:")
        for error in sorted(unknown_errors) :
            print(f"  - {error}")

    if errors_without_causes :
        print(f"\n❌ Errors that have no causes defined in diagnoses files:")
        for error in sorted(errors_without_causes) :
            print(f"  - {error}")

    if errors_with_invalid_causes :
        print(f"\n❌ Errors that have invalid cause structures in diagnoses files:")
        for error in sorted(errors_with_invalid_causes) :
            msg = f"(missing component/problem or probability/frequency keys)"
            print(f"  - {error} {msg}")

    return False

def check_diagnoses_components_problems( directory : str, system_type : str) -> bool :
    """
    Check that all components and problems referenced in diagnoses files exist in their respective files.
    """
    
    # Load all data using the new loader function
    data = load_domain_knowledge(directory)
    
    # Track issues
    invalid_causes = []
    missing_components = []
    missing_problems = []

    # Check each error and its causes
    for error_code, causes_list in data['diagnoses'].items() :
        for i, cause in enumerate(causes_list) :
            if not isinstance( cause, dict) :
                invalid_causes.append((error_code, i, "not a dictionary"))
                continue

            # Check if it's a component cause
            if 'component' in cause :
                component_name = cause['component']
                if component_name not in data['components'] :
                    missing_components.append((error_code, i, component_name))
            
            # Check if it's a problem cause (any key starting with 'problem_')
            problem_keys = [ key for key in cause.keys() if str(key).startswith('problem_') ]
            for problem_key in problem_keys :
                problem_name = cause[problem_key]
                if problem_name not in data['problems'] :
                    missing_problems.append((error_code, i, problem_name))

    # Print results
    if not (invalid_causes or missing_components or missing_problems) :
        print("✅ All components and problems in diagnoses are properly defined!")
        return True

    if invalid_causes :
        print(f"❌ Invalid cause structures in diagnoses files:")
        for error_code, cause_index, reason in invalid_causes :
            print(f"  - {error_code} (cause {cause_index}): {reason}")

    if missing_components :
        print(f"❌ Components referenced in diagnoses files but not defined in components files:")
        for error_code, cause_index, component_name in missing_components :
            print(f"  - {error_code} (cause {cause_index}): {component_name}")

    if missing_problems :
        print(f"❌ Problems referenced in diagnoses files but not defined in problems files:")
        for error_code, cause_index, problem_name in missing_problems :
            print(f"  - {error_code} (cause {cause_index}): {problem_name}")

    return False

if __name__ == "__main__" :

    dir_input = DIR_DKNOWLEDGE_B
    usage_msg = f"Usage: python check_errors_diagnoses.py [{'|'.join(SUBSYSTEMS)}]"

    if not os.path.isdir(dir_input) :
        print(f"❌ Error: Directory '{dir_input}' does not exist")
        sys.exit(1)
    
    if len(sys.argv) != 2 :
        print(usage_msg)
        sys.exit(1)
    
    subsystem_input = sys.argv[1]
    
    if subsystem_input not in SUBSYSTEMS :
        print(usage_msg)
        sys.exit(1)
    
    print(f"Directory: {dir_input}")
    print(f"System type: {subsystem_input}")
    print(f"Checking maps from errors to diagnoses...")
    check_error_mappings( dir_input, subsystem_input)
    print(f"Checking maps from diagnoses to components/problems...")
    check_diagnoses_components_problems( dir_input, subsystem_input)
