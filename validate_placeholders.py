import json
import sys
from pathlib import Path

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_sets(sets):
    """
    Validate that each set is a dict with a single key and a comma-separated string of values.
    Returns a dict mapping set names to sets of values.
    """
    set_map = {}
    errors = []
    for s in sets:
        if not isinstance(s, dict) or len(s) != 1:
            errors.append(f"❌ Invalid set entry (should be a dict with one key): {s}")
            continue
        set_name, values = next(iter(s.items()))
        if not isinstance(values, str):
            errors.append(f"❌ Set '{set_name}' values should be a comma-separated string.")
            continue
        value_set = set(v.strip() for v in values.split(',') if v.strip())
        if not value_set:
            errors.append(f"❌ Set '{set_name}' has no values.")
            continue
        set_map[set_name] = value_set
    return set_map, errors

def parse_function_signature(sig):
    """
    Parse function signature like 'FUNC(ARGSET)' into (FUNC, ARGSET).
    """
    if not sig.endswith(')') or '(' not in sig:
        return None, None
    func_name = sig[:sig.index('(')]
    arg_set = sig[sig.index('(')+1:-1]
    return func_name, arg_set

def validate_functions(functions, set_map):
    errors = []
    for f in functions:
        if not isinstance(f, dict) or len(f) != 1:
            errors.append(f"❌ Invalid function entry (should be a dict with one key): {f}")
            continue
        sig, mapping = next(iter(f.items()))
        func_name, arg_set = parse_function_signature(sig)
        if not func_name or not arg_set:
            errors.append(f"❌ Invalid function signature: '{sig}'")
            continue
        if arg_set not in set_map:
            errors.append(f"❌ Function '{sig}' refers to undefined set '{arg_set}'.")
            continue
        arg_values = set_map[arg_set]
        if not isinstance(mapping, dict):
            errors.append(f"❌ Function '{sig}' mapping should be a dict.")
            continue
        # Check that every value in the argument set is mapped
        missing = arg_values - set(mapping.keys())
        if missing:
            errors.append(f"❌ Function '{sig}' missing mappings for: {sorted(missing)}")
        # Optionally: check that every mapping value is non-empty
        for k, v in mapping.items():
            if not v or (isinstance(v, str) and not v.strip()):
                errors.append(f"❌ Function '{sig}' maps '{k}' to an empty value.")
    return errors

def main():
    placeholder_path = Path(__file__).parent / 'json' / 'placeholders.json'
    try:
        data = load_json_file(placeholder_path)
    except Exception as e:
        print(f"❌ Error loading {placeholder_path}: {e}")
        sys.exit(1)

    sets = data.get('sets', [])
    functions = data.get('functions', [])

    set_map, set_errors = validate_sets(sets)
    func_errors = validate_functions(functions, set_map)

    if set_errors or func_errors:
        for err in set_errors + func_errors:
            print(err)
        print("\n❌ Validation failed.")
        sys.exit(1)
    else:
        print("✅ All sets and functions in placeholders.json are valid!")
        sys.exit(0)

if __name__ == "__main__":
    main() 