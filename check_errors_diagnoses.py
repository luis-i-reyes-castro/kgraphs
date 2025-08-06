#!/usr/bin/env python3
"""
Check error mappings for consistency
"""

import sys
import utilities as util

def has_valid_cause_keys( cause : dict) -> bool :
    # Cause must have either a component or a problem
    cond_1A = 'component' in cause
    cond_1B = any( str(key).startswith('problem_') for key in cause.keys() )
    # Cause must have a probability or frequency
    cond_2_vals = ( 'probability', 'frequency' )
    cond_2      = any( key in cause for key in cond_2_vals )
    # Enforce conditions
    if not ( ( cond_1A or cond_1B ) and cond_2 ) :
        return False
    return True

def check_error_mappings( system_type : str) -> bool :
    # Construct filenames based on system_type
    errors_file = f'expansions/errors_{system_type}.json'
    causes_file = f'expansions/diagnoses_{system_type}.json'

    # Load both JSON files
    try:
        errors       = util.load_json_file(errors_file)
        error_causes = util.load_json_file(causes_file)
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file {e.filename}")
        return False

    # Get all error codes from errors file
    all_error_codes = set(errors.keys())

    # Create sets to track various conditions
    found_errors = set()
    errors_without_causes = set()
    errors_with_invalid_causes = set()

    # Go through each error in error_causes
    for error_code, causes_list in error_causes.items():
        found_errors.add(error_code)
        
        # Check if the error has causes
        if not causes_list:
            errors_without_causes.add(error_code)
            continue
            
        # Check if each cause has the required keys
        for i, cause in enumerate(causes_list):
            if not isinstance(cause, dict):
                errors_with_invalid_causes.add(error_code)
                break
            if not has_valid_cause_keys(cause):
                errors_with_invalid_causes.add(error_code)
                break

    # Find errors that are in errors file but not in causes file
    missing_errors = all_error_codes - found_errors

    # Find errors that are in causes file but not in errors file
    unknown_errors = found_errors - all_error_codes

    # Print results
    if not (missing_errors or unknown_errors or errors_without_causes or errors_with_invalid_causes):
        print("✅ All errors are properly mapped exactly once with valid causes!")
        return True

    if missing_errors:
        print(f"\n❌ Errors present in {errors_file} but missing from {causes_file}:")
        for error in sorted(missing_errors):
            print(f"  - {error}")

    if unknown_errors:
        print(f"\n❌ Errors present in {causes_file} but not defined in {errors_file}:")
        for error in sorted(unknown_errors):
            print(f"  - {error}")

    if errors_without_causes:
        print(f"\n❌ Errors that have no causes defined in {causes_file}:")
        for error in sorted(errors_without_causes):
            print(f"  - {error}")

    if errors_with_invalid_causes:
        print(f"\n❌ Errors that have invalid cause structures in {causes_file}:")
        for error in sorted(errors_with_invalid_causes):
            msg = f"(missing component/problem or probability/frequency keys)"
            print(f"  - {error} {msg}")

    return False

if __name__ == "__main__":

    available_systems = ['spraying', 'propulsion', 'flight']

    if len(sys.argv) != 2 or sys.argv[1] not in available_systems :
        print(f"Usage: python check_error_mappings.py [{'|'.join(available_systems)}]")
        sys.exit(1)
    
    check_error_mappings(sys.argv[1])
