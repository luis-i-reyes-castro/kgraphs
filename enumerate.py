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
    result = OrderedDict()
    for orig_key, orig_val in d.items():
        set_phs = find_set_placeholders(orig_key)
        if set_phs:
            set_name = set_phs[0]
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

def expand_value(val, set_context, set_map, func_map):
    if isinstance(val, str):
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
        expanded = OrderedDict()
        for d in data:
            expanded.update(expand_top_level_dict(d, set_map, func_map))
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
