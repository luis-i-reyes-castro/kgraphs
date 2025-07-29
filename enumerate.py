import json
import sys
from pathlib import Path
import re
import itertools
from collections import OrderedDict

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_placeholders():
    placeholder_path = Path(__file__).parent / 'json' / 'placeholders.json'
    data = load_json_file(placeholder_path)
    # Build set map
    set_map = {}
    for s in data.get('sets', []):
        if isinstance(s, dict) and len(s) == 1:
            set_name, values = next(iter(s.items()))
            set_map[set_name] = [v.strip() for v in values.split(',') if v.strip()]
    # Build function map
    func_map = {}
    for f in data.get('functions', []):
        if isinstance(f, dict) and len(f) == 1:
            sig, mapping = next(iter(f.items()))
            func_map[sig] = mapping
    return set_map, func_map

def find_set_placeholders(s):
    # Matches (SETNAME)
    return re.findall(r'\((\w+)\)', s)

def find_function_placeholders(s):
    # Matches (FUNCTION(SETNAME))
    return re.findall(r'\((\w+\(\w+\))\)', s)

def expand_top_level_dict(d, set_map, func_map):
    # Check if any keys contain placeholders
    has_placeholders_in_keys = False
    placeholder_sets_in_keys = set()
    
    # Check if any values contain placeholders
    has_placeholders_in_values = False
    placeholder_sets_in_values = set()
    
    # Check if any values contain set-returning functions
    has_set_returning_functions = False
    
    for orig_key, orig_val in d.items():
        set_phs_in_key = find_set_placeholders(orig_key)
        if set_phs_in_key:
            has_placeholders_in_keys = True
            placeholder_sets_in_keys.update(set_phs_in_key)
        
        set_phs_in_val = find_set_placeholders(str(orig_val))
        if set_phs_in_val:
            has_placeholders_in_values = True
            placeholder_sets_in_values.update(set_phs_in_val)
        
        # Check for set-returning functions in values
        if isinstance(orig_val, str):
            func_calls = re.findall(r'\((\w+\(\w+\))\)', orig_val)
            for func_sig in func_calls:
                m = re.match(r'(\w+)\((\w+)\)', func_sig)
                if m:
                    func_name, arg_set = m.group(1), m.group(2)
                    if arg_set in set_map:
                        mapping = func_map.get(func_sig, {})
                        for set_val in set_map[arg_set]:
                            result_val = mapping.get(set_val, '')
                            if ',' in result_val:
                                has_set_returning_functions = True
                                break
                        if has_set_returning_functions:
                            break
                if has_set_returning_functions:
                    break
    
    # If placeholders in keys, use original logic
    if has_placeholders_in_keys:
        result = OrderedDict()
        for orig_key, orig_val in d.items():
            set_phs_in_key = find_set_placeholders(orig_key)
            if set_phs_in_key:
                set_name = set_phs_in_key[0]
                if set_name not in set_map:
                    continue
                for set_val in set_map[set_name]:
                    new_key = re.sub(r'\(' + re.escape(set_name) + r'\)', f'{set_val}', orig_key)
                    new_val = expand_value(orig_val, {set_name: set_val}, set_map, func_map)
                    result[new_key] = new_val
            else:
                new_val = expand_value(orig_val, {}, set_map, func_map)
                result[orig_key] = new_val
        return result
    
    # If set-returning functions in values, handle them specially
    if has_set_returning_functions:
        result = []
        
        # Find all placeholder sets that could be used in set-returning functions
        all_placeholder_sets = set()
        for orig_key, orig_val in d.items():
            if isinstance(orig_val, str):
                func_calls = re.findall(r'\((\w+\(\w+\))\)', orig_val)
                for func_sig in func_calls:
                    m = re.match(r'(\w+)\((\w+)\)', func_sig)
                    if m:
                        func_name, arg_set = m.group(1), m.group(2)
                        if arg_set in set_map:
                            all_placeholder_sets.add(arg_set)
        
        # For each value of each placeholder set, create expansions
        for set_name in all_placeholder_sets:
            for set_val in set_map[set_name]:
                new_obj = OrderedDict()
                for orig_key, orig_val in d.items():
                    new_val = expand_value(orig_val, {set_name: set_val}, set_map, func_map)
                    # If expand_value returns a list, create separate objects for each value
                    if isinstance(new_val, list):
                        for val in new_val:
                            new_obj_copy = new_obj.copy()
                            new_obj_copy[orig_key] = val
                            result.append(new_obj_copy)
                        break  # Only process this key once since we're creating multiple objects
                    else:
                        new_obj[orig_key] = new_val
                else:
                    # No list returns, add the object
                    result.append(new_obj)
        
        return result
    
    # If placeholders only in values, handle based on value types
    if has_placeholders_in_values:
        # Find the first placeholder set that appears in values
        first_placeholder_set = None
        for set_name in placeholder_sets_in_values:
            if set_name in set_map:
                first_placeholder_set = set_name
                break
        
        if first_placeholder_set is None:
            # No valid placeholder sets found
            result_dict = OrderedDict()
            for orig_key, orig_val in d.items():
                new_val = expand_value(orig_val, {}, set_map, func_map)
                result_dict[orig_key] = new_val
            return result_dict
        
        # Check if any value is a list (like in test2.json)
        has_list_values = any(isinstance(val, list) for val in d.values())
        
        if has_list_values:
            # For lists, expand placeholders within the list elements
            result = OrderedDict()
            for orig_key, orig_val in d.items():
                if isinstance(orig_val, list):
                    # Expand placeholders within list elements
                    expanded_list = []
                    for item in orig_val:
                        if isinstance(item, dict):
                            # Check if this dict item has placeholders
                            item_has_placeholders = False
                            item_placeholder_sets = set()
                            for item_key, item_val in item.items():
                                set_phs = find_set_placeholders(str(item_val))
                                if set_phs:
                                    item_has_placeholders = True
                                    item_placeholder_sets.update(set_phs)
                            
                            if item_has_placeholders:
                                # Find the first placeholder set
                                first_item_placeholder_set = None
                                for set_name in item_placeholder_sets:
                                    if set_name in set_map:
                                        first_item_placeholder_set = set_name
                                        break
                                
                                if first_item_placeholder_set:
                                    # Create separate items for each placeholder expansion
                                    for set_val in set_map[first_item_placeholder_set]:
                                        expanded_item = {}
                                        for item_key, item_val in item.items():
                                            expanded_item_val = expand_value(item_val, {first_item_placeholder_set: set_val}, set_map, func_map)
                                            # Check if expand_value returned a list (set-returning function)
                                            if isinstance(expanded_item_val, list):
                                                # Create separate items for each value
                                                for val in expanded_item_val:
                                                    expanded_item_copy = expanded_item.copy()
                                                    expanded_item_copy[item_key] = val
                                                    expanded_list.append(expanded_item_copy)
                                                break  # Only process this key once since we're creating multiple items
                                            else:
                                                expanded_item[item_key] = expanded_item_val
                                        else:
                                            # No list returns, add the item
                                            expanded_list.append(expanded_item)
                                else:
                                    # No valid placeholder sets, expand normally
                                    expanded_item = {}
                                    for item_key, item_val in item.items():
                                        expanded_item_val = expand_value(item_val, {}, set_map, func_map)
                                        expanded_item[item_key] = expanded_item_val
                                    expanded_list.append(expanded_item)
                            else:
                                # Check for set-returning functions even if no placeholders
                                item_has_set_returning_functions = False
                                for item_key, item_val in item.items():
                                    if isinstance(item_val, str):
                                        func_calls = re.findall(r'\((\w+\(\w+\))\)', item_val)
                                        for func_sig in func_calls:
                                            m = re.match(r'(\w+)\((\w+)\)', func_sig)
                                            if m:
                                                func_name, arg_set = m.group(1), m.group(2)
                                                if arg_set in set_map:
                                                    mapping = func_map.get(func_sig, {})
                                                    for set_val in set_map[arg_set]:
                                                        result_val = mapping.get(set_val, '')
                                                        if ',' in result_val:
                                                            item_has_set_returning_functions = True
                                                            break
                                                    if item_has_set_returning_functions:
                                                        break
                                        if item_has_set_returning_functions:
                                            break
                                
                                if item_has_set_returning_functions:
                                    # Handle set-returning functions by creating separate items
                                    # Find all placeholder sets that could be used in set-returning functions
                                    all_item_placeholder_sets = set()
                                    for item_key, item_val in item.items():
                                        if isinstance(item_val, str):
                                            func_calls = re.findall(r'\((\w+\(\w+\))\)', item_val)
                                            for func_sig in func_calls:
                                                m = re.match(r'(\w+)\((\w+)\)', func_sig)
                                                if m:
                                                    func_name, arg_set = m.group(1), m.group(2)
                                                    if arg_set in set_map:
                                                        all_item_placeholder_sets.add(arg_set)
                                    
                                    # For each value of each placeholder set, create expansions
                                    for set_name in all_item_placeholder_sets:
                                        for set_val in set_map[set_name]:
                                            expanded_item = {}
                                            for item_key, item_val in item.items():
                                                expanded_item_val = expand_value(item_val, {set_name: set_val}, set_map, func_map)
                                                # If expand_value returns a list, create separate items for each value
                                                if isinstance(expanded_item_val, list):
                                                    for val in expanded_item_val:
                                                        expanded_item_copy = expanded_item.copy()
                                                        expanded_item_copy[item_key] = val
                                                        expanded_list.append(expanded_item_copy)
                                                    break  # Only process this key once since we're creating multiple items
                                                else:
                                                    expanded_item[item_key] = expanded_item_val
                                            else:
                                                # No list returns, add the item
                                                expanded_list.append(expanded_item)
                                else:
                                    # No placeholders or set-returning functions, expand normally
                                    expanded_item = {}
                                    for item_key, item_val in item.items():
                                        expanded_item_val = expand_value(item_val, {}, set_map, func_map)
                                        expanded_item[item_key] = expanded_item_val
                                    expanded_list.append(expanded_item)
                        else:
                            # Non-dict item, expand placeholders directly
                            expanded_item = expand_value(item, {}, set_map, func_map)
                            expanded_list.append(expanded_item)
                    result[orig_key] = expanded_list
                else:
                    # Non-list value, expand normally
                    new_val = expand_value(orig_val, {}, set_map, func_map)
                    result[orig_key] = new_val
            return result
        else:
            # For non-list values, create separate objects for each expansion
            result = []
            for set_val in set_map[first_placeholder_set]:
                new_obj = OrderedDict()
                for orig_key, orig_val in d.items():
                    new_val = expand_value(orig_val, {first_placeholder_set: set_val}, set_map, func_map)
                    new_obj[orig_key] = new_val
                result.append(new_obj)
            return result
    
    # No placeholders found
    result = OrderedDict()
    for orig_key, orig_val in d.items():
        new_val = expand_value(orig_val, {}, set_map, func_map)
        result[orig_key] = new_val
    return result

def expand_value(val, set_context, set_map, func_map):
    if isinstance(val, str):
        # Check if there are any function calls that return sets
        func_calls = re.findall(r'\((\w+\(\w+\))\)', val)
        has_set_returning_functions = False
        
        for func_sig in func_calls:
            m = re.match(r'(\w+)\((\w+)\)', func_sig)
            if m:
                func_name, arg_set = m.group(1), m.group(2)
                arg_val = set_context.get(arg_set)
                if arg_val is not None:
                    mapping = func_map.get(func_sig, {})
                    result_val = mapping.get(arg_val, '')
                    # Check if the function returns multiple values (comma-separated)
                    if ',' in result_val:
                        has_set_returning_functions = True
                        break
        
        if has_set_returning_functions:
            # Handle functions that return sets by creating multiple expansions
            results = []
            
            # Find all function calls and their possible expansions
            func_expansions = []
            for func_sig in func_calls:
                m = re.match(r'(\w+)\((\w+)\)', func_sig)
                if m:
                    func_name, arg_set = m.group(1), m.group(2)
                    arg_val = set_context.get(arg_set)
                    if arg_val is not None:
                        mapping = func_map.get(func_sig, {})
                        result_val = mapping.get(arg_val, '')
                        if ',' in result_val:
                            # Function returns multiple values
                            func_values = [v.strip() for v in result_val.split(',') if v.strip()]
                            func_expansions.append((func_sig, func_values))
                        else:
                            # Function returns single value
                            func_expansions.append((func_sig, [result_val]))
                    else:
                        # Function argument not in context, keep as is
                        func_expansions.append((func_sig, [f'({func_sig})']))
                else:
                    # Not a valid function call, keep as is
                    func_expansions.append((func_sig, [f'({func_sig})']))
            
            # Generate all combinations of function expansions
            import itertools
            func_names = [exp[0] for exp in func_expansions]
            func_value_lists = [exp[1] for exp in func_expansions]
            
            for combination in itertools.product(*func_value_lists):
                expanded_val = val
                for func_sig, replacement in zip(func_names, combination):
                    expanded_val = re.sub(r'\(' + re.escape(func_sig) + r'\)', replacement, expanded_val)
                
                # Also replace any remaining set placeholders
                for set_name, set_val in set_context.items():
                    expanded_val = re.sub(r'\(' + re.escape(set_name) + r'\)', f'{set_val}', expanded_val)
                
                results.append(expanded_val)
            
            return results
        else:
            # No set-returning functions, use original logic
            # 1. Replace all function calls (FUNCTION(SET)) with their mapped value
            def func_replacer(match):
                func_sig = match.group(1)
                m = re.match(r'(\w+)\((\w+)\)', func_sig)
                if m:
                    func_name, arg_set = m.group(1), m.group(2)
                    arg_val = set_context.get(arg_set)
                    if arg_val is not None:
                        mapping = func_map.get(func_sig, {})
                        return mapping.get(arg_val, '')
                return match.group(0)  # leave unchanged if not found
            val = re.sub(r'\((\w+\(\w+\))\)', func_replacer, val)
            # 2. Replace set placeholders
            for set_name, set_val in set_context.items():
                val = re.sub(r'\(' + re.escape(set_name) + r'\)', f'{set_val}', val)
            return val
    elif isinstance(val, dict):
        return {k: expand_value(v, set_context, set_map, func_map) for k, v in val.items()}
    elif isinstance(val, list):
        return [expand_value(v, set_context, set_map, func_map) for v in val]
    else:
        return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python enum_json.py <input_json_file>")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ Input file {input_path} does not exist.")
        sys.exit(1)
    set_map, func_map = load_placeholders()
    data = load_json_file(input_path)
    if isinstance(data, list):
        expanded_list = []
        for d in data:
            expanded_items = expand_top_level_dict(d, set_map, func_map)
            if isinstance(expanded_items, list):
                # Multiple objects returned
                expanded_list.extend(expanded_items)
            else:
                # Single object returned
                expanded_list.append(expanded_items)
        expanded = expanded_list
    elif isinstance(data, dict):
        expanded = expand_top_level_dict(data, set_map, func_map)
    else:
        print("❌ Input JSON must be a dict or list of dicts.")
        sys.exit(1)
    out_dir = Path(__file__).parent / 'enum'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / input_path.name
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(expanded, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"✅ Wrote enumerated cases to {out_path}")

if __name__ == "__main__":
    main()
