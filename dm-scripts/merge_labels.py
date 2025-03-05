import csv
import subprocess
import tempfile
import os

# Configuration
ORIGINAL_CSV = "/home/luis/kgraphs/labels_DAL.csv"
POSITIVE_CSV = "/home/luis/kgraphs/labels_DAL_positive.csv"
EMPTY_CSV = "/home/luis/kgraphs/labels_DAL_empty.csv"

def load_csv(filename):
    """Load CSV file into a dictionary"""
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    data[row[0]] = row[1:]
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return data

def reconcile_rotation(original_rotation, new_rotation):
    """Reconcile rotation between original and new states"""
    orig = int(original_rotation) if original_rotation else 0
    new = int(new_rotation) if new_rotation else 0
    
    if new == 0:
        return orig
    return (orig + new) % 360

def main():
    # Load data from all CSV files
    original_data = load_csv(ORIGINAL_CSV)
    positive_data = load_csv(POSITIVE_CSV)
    empty_data = load_csv(EMPTY_CSV)
    
    # Create a dictionary of changes to apply
    changes = {}
    
    # Process positive data
    for filename, new_row in positive_data.items():
        if filename in original_data:
            original_row = original_data[filename]
            rotation = reconcile_rotation(original_row[0], new_row[0])
            merged_row = [str(rotation)] + new_row[1:]
            if merged_row != original_row:
                changes[filename] = merged_row
    
    # Process empty data
    for filename, new_row in empty_data.items():
        if filename in original_data:
            original_row = original_data[filename]
            rotation = reconcile_rotation(original_row[0], new_row[0])
            merged_row = [str(rotation), "", "", ""]
            if merged_row != original_row:
                changes[filename] = merged_row
    
    # Print changes that will be made
    print("\nChanges to be applied:")
    print("-" * 80)
    for filename, new_row in changes.items():
        original_row = original_data.get(filename, ["0", "", "", ""])
        print(f"{filename},{','.join(original_row)} ->")
        print(f"{filename},{','.join(new_row)}")
    
    if not changes:
        print("No changes to apply.")
        return
    
    # Create a sed script to apply the changes
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as sed_script:
        for filename, new_row in changes.items():
            # Escape special characters in the filename for sed
            escaped_filename = filename.replace('/', '\\/').replace('.', '\\.').replace('_', '\\_')
            # Create the replacement line
            new_line = f"{filename},{','.join(new_row)}"
            # Write the sed command - note the correct syntax
            sed_script.write(f"s/^{escaped_filename},.*/{new_line}/\n")
    
    # Apply the changes using sed
    try:
        subprocess.run(["sed", "-i", "-f", sed_script.name, ORIGINAL_CSV], check=True)
        print(f"\nSuccessfully applied {len(changes)} changes to {ORIGINAL_CSV}")
    except subprocess.CalledProcessError as e:
        print(f"Error applying changes: {e}")
    finally:
        # Clean up the temporary file
        os.unlink(sed_script.name)

if __name__ == "__main__":
    main()
