import json
import sys

def load_json_file(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def validate_error_mappings(system_type):
    # Construct filenames based on system_type
    errors_file = f'T40_errors_{system_type}.json'
    causes_file = f'T40_error_causes_{system_type}.json'

    # Load both JSON files
    try:
        errors = load_json_file(errors_file)
        error_causes = load_json_file(causes_file)
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file {e.filename}")
        return False

    # Get all error codes from T40_errors file
    all_error_codes = set(errors.keys())

    # Create sets to track various conditions
    found_errors = set()
    duplicate_errors = set()
    errors_without_causes = set()

    # Go through each error group in error_causes
    for error_group in error_causes[f'T40_error_causes_{system_type}']:
        if 'errors' not in error_group:
            continue
            
        # Check if the error group has causes
        if 'causes' not in error_group or not error_group['causes']:
            errors_without_causes.update(error_group['errors'])
            
        for error in error_group['errors']:
            if error in found_errors:
                duplicate_errors.add(error)
            found_errors.add(error)

    # Find errors that are in errors file but not in causes file
    missing_errors = all_error_codes - found_errors

    # Find errors that are in causes file but not in errors file
    unknown_errors = found_errors - all_error_codes

    # Print results
    if not (missing_errors or unknown_errors or duplicate_errors or errors_without_causes):
        print("✅ All errors are properly mapped exactly once with causes!")
        return True

    if missing_errors:
        print(f"\n❌ Errors present in {errors_file} but missing from {causes_file}:")
        for error in sorted(missing_errors):
            print(f"  - {error}")

    if unknown_errors:
        print(f"\n❌ Errors present in {causes_file} but not defined in {errors_file}:")
        for error in sorted(unknown_errors):
            print(f"  - {error}")

    if duplicate_errors:
        print(f"\n❌ Errors that appear multiple times in {causes_file}:")
        for error in sorted(duplicate_errors):
            print(f"  - {error}")

    if errors_without_causes:
        print(f"\n❌ Errors that have no causes defined in {causes_file}:")
        for error in sorted(errors_without_causes):
            print(f"  - {error}")

    return False

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['spraying', 'propulsion', 'flight']:
        print("Usage: python validate_error_mappings.py [spraying|propulsion|flight]")
        sys.exit(1)
    
    validate_error_mappings(sys.argv[1])
