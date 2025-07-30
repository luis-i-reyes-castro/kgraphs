from collections import OrderedDict
from json import load as json_load
from pathlib import Path
import re
import regex_constants as rxconst

def load_json_file( filepath : str) -> OrderedDict:
    with open( filepath, 'r', encoding='utf-8') as f:
        return json_load( f, object_pairs_hook = OrderedDict)

def isvalid_set( set_values : list) -> bool:
    # Check that set_values is not empty
    if not set_values:
        return False
    # Check that all set values are of the same type
    first_type = type(set_values[0])
    if not all( isinstance( val, first_type) for val in set_values ):
        return False
    # No check failed so set is valid
    return True

def isvalid_fun( sig : str, mapping : dict, set_map : dict) -> bool:
    # Extract the function argument from sig using RX_ARG
    match = re.search( rxconst.RX_ARG, sig)
    set_name = match.group(1) if match else None
    # Check that set_name is in set_map and extract its values
    if not set_name:
        return False
    if set_name not in set_map:
        return False
    set_values = set_map[set_name]
    # Check that mapping has the same number of keys as set_values has elements
    if len(mapping) != len(set_values):
        return False
    # Check that every key in mapping is in set_values
    if not all(key in set_values for key in mapping.keys()):
        return False
    # No check failed so function is valid
    return True

def isvalid_rel( sig : str, mapping : dict, set_map : dict) -> bool:
    # Use isvalid_fun to check that the keys of the mapping
    if not isvalid_fun(sig, mapping, set_map):
        return False
    # Check that every value in the mapping is a valid set
    for val in mapping.values():
        if not isvalid_set(val):
            return False
    return True

def load_placeholders( dir: str = 'newlang',
                       file: str = 'placeholders.json'
                     ) -> tuple[dict, dict, dict]:
    # Load data
    placeholder_path = Path(__file__).parent / dir / file
    data = load_json_file(placeholder_path)
    # Build set map
    set_map = {}
    for s in data.get('sets', []):
        if isinstance(s, dict) and len(s) == 1:
            set_name, values = next(iter(s.items()))
            if not isvalid_set(values):
                print(f"Error: Set '{set_name}' is invalid: {values}")
            set_map[set_name] = values
    # Build function map
    fun_map = {}
    for f in data.get('functions', []):
        if isinstance(f, dict) and len(f) == 1:
            sig, mapping = next(iter(f.items()))
            if not isvalid_fun(sig, mapping, set_map):
                print(f"Error: Function '{sig}' is invalid: {mapping}")
            fun_map[sig] = mapping
    # Build relation map
    rel_map = {}
    for r in data.get('relations', []):
        if isinstance(r, dict) and len(r) == 1:
            sig, mapping = next(iter(r.items()))
            if not isvalid_rel(sig, mapping, set_map):
                print(f"Error: Relation '{sig}' is invalid: {mapping}")
            rel_map[sig] = mapping
    # Return maps
    return set_map, fun_map, rel_map

def get_signatures( set_map : dict,
                    fun_map : dict,
                    rel_map : dict) -> tuple[set, set, set]:
    # Get all names
    sets = set(set_map.keys())
    funs = set(fun_map.keys())
    rels = set(rel_map.keys())
    # Add sets referenced in functions
    for fun_sig in fun_map.keys():
        arg_set = extract_arg_set(fun_sig)
        if arg_set:
            sets.update(arg_set)
    # Add sets referenced in relations
    for rel_sig in rel_map.keys():
        arg_set = extract_arg_set(rel_sig)
        if arg_set:
            sets.update(arg_set)
    # Return signatures
    return sets, funs, rels

def get_placeholders( keyval : str, signatures : tuple[list]) -> tuple[list]:
    # Load signatures
    sets = signatures[0]
    funs = signatures[1]
    rels = signatures[2]
    # Get all sets, funs and rels in keyval
    ph_sets = re.findall( rxconst.RX_SET_, keyval)
    ph_funs = re.findall( rxconst.RX_FUN_, keyval)
    ph_rels = re.findall( rxconst.RX_REL_, keyval)
    # Reconstruct full signatures from captured groups
    ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
    ph_rels_full = [f"{rel_name}[{arg_name}]" for rel_name, arg_name in ph_rels]
    # Check that sets, funs and rels in keyval are valid
    for ph in ph_sets:
        if ph not in sets:
            print(f"Error: Set '{ph}' not found in signatures")
    for ph in ph_funs_full:
        if ph not in funs:
            print(f"Error: Function '{ph}' not found in signatures")
    for ph in ph_rels_full:
        if ph not in rels:
            print(f"Error: Relation '{ph}' not found in signatures")
    # Return lists
    return ph_sets, ph_funs_full, ph_rels_full

def replace_placeholder( val_orig : str, val_new : str, sig : str) -> str:
    return val_orig.replace( f'({sig})', val_new)

def extract_arg_set(sig : str) -> str:
    """
    Extract the argument set name from a function or relation signature.
    For example, from "ENG[SIDE]" extract "SIDE".
    """
    match = re.search( rxconst.RX_ARG, sig)
    return match.group(1) if match else None
