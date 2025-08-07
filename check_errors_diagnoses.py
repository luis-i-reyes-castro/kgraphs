#!/usr/bin/env python3
"""
Check error mappings for consistency
"""

import parsing_utilities as pu
import sys
import utilities as util
import glob
import os

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
            if not pu.has_valid_cause_keys(cause):
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

def check_diagnoses_components_problems(system_type: str) -> bool:
    """
    Check that all components and problems referenced in diagnoses files exist in their respective files.
    """
    # Load diagnoses file
    diagnoses_file = f'expansions/diagnoses_{system_type}.json'
    try:
        diagnoses = util.load_json_file(diagnoses_file)
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file {e.filename}")
        return False

    # Load all components files into a single dictionary
    components = {}
    components_files = glob.glob('expansions/components_*.json')
    for file_path in components_files:
        try:
            file_components = util.load_json_file(file_path)
            components.update(file_components)
        except FileNotFoundError as e:
            print(f"❌ Error: Could not find file {e.filename}")
            return False

    # Load all problems files into a single dictionary
    problems = {}
    problems_files = glob.glob('expansions/problems_*.json')
    for file_path in problems_files:
        try:
            file_problems = util.load_json_file(file_path)
            problems.update(file_problems)
        except FileNotFoundError as e:
            print(f"❌ Error: Could not find file {e.filename}")
            return False

    # Track issues
    invalid_causes = []
    missing_components = []
    missing_problems = []

    # Check each error and its causes
    for error_code, causes_list in diagnoses.items():
        for i, cause in enumerate(causes_list):
            if not isinstance(cause, dict):
                invalid_causes.append((error_code, i, "not a dictionary"))
                continue

            # Check if it's a component cause
            if 'component' in cause:
                component_name = cause['component']
                if component_name not in components:
                    missing_components.append((error_code, i, component_name))
            
            # Check if it's a problem cause (any key starting with 'problem_')
            problem_keys = [key for key in cause.keys() if str(key).startswith('problem_')]
            for problem_key in problem_keys:
                problem_name = cause[problem_key]
                if problem_name not in problems:
                    missing_problems.append((error_code, i, problem_name))

    # Print results
    if not (invalid_causes or missing_components or missing_problems):
        print("✅ All components and problems in diagnoses are properly defined!")
        return True

    if invalid_causes:
        print(f"\n❌ Invalid cause structures in {diagnoses_file}:")
        for error_code, cause_index, reason in invalid_causes:
            print(f"  - {error_code} (cause {cause_index}): {reason}")

    if missing_components:
        print(f"\n❌ Components referenced in {diagnoses_file} but not defined in components files:")
        for error_code, cause_index, component_name in missing_components:
            print(f"  - {error_code} (cause {cause_index}): {component_name}")

    if missing_problems:
        print(f"\n❌ Problems referenced in {diagnoses_file} but not defined in problems files:")
        for error_code, cause_index, problem_name in missing_problems:
            print(f"  - {error_code} (cause {cause_index}): {problem_name}")

    return False

if __name__ == "__main__":

    available_systems = ['spraying', 'propulsion', 'flight']

    if len(sys.argv) != 2 or sys.argv[1] not in available_systems :
        print(f"Usage: python check_error_mappings.py [{'|'.join(available_systems)}]")
        sys.exit(1)
    
    system_type = sys.argv[1]
    
    print(f"Checking error mappings for {system_type}...")
    check_error_mappings(system_type)
    
    print(f"Checking diagnoses components and problems for {system_type}...")
    check_diagnoses_components_problems(system_type)
