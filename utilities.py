from collections import OrderedDict
from json import load as json_load
from pathlib import Path
import re
import regex_constants as rxconst

def load_json_file( filepath : str) -> OrderedDict:
    """
    Load JSON file as OrderedDict
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return json_load( f, object_pairs_hook = OrderedDict)

def isvalid_set( set_values : list) -> bool:
    """
    Check placeholder declaration for correctness: sets
    """
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
    """
    Check placeholder declaration for correctness: functions
    """
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
    """
    Check placeholder declaration for correctness: relations
    """
    # Use isvalid_fun to check that the keys of the mapping
    if not isvalid_fun(sig, mapping, set_map):
        return False
    # Check that every value in the mapping is a valid set
    for val in mapping.values():
        if not isvalid_set(val):
            return False
    return True

def extract_arg_set( sig : str) -> str:
    """
    Extract the argument set name from a function or relation signature.
    For example, from "ENG[SIDE]" extract "SIDE".
    """
    match = re.search( rxconst.RX_ARG, sig)
    return match.group(1) if match else None

# def extract_arg_map( fun_rel_map : dict) -> dict:
#     result = {}
#     for k in fun_rel_map.keys():
#         result[k] = extract_arg_set(k)
#     return result

def replace_placeholder( val_orig : str, val_new : str, sig : str) -> str:
    """
    Replace a placeholder with a new value
    """
    return val_orig.replace( f'({sig})', val_new)

class placeholderData:
    """
    Convenience object for storing all placeholder data
    """
    
    def __init__(self, set_map : dict = {}, fun_map : dict = {}, rel_map : dict = {}):
        """
        Initialize placeholder data
        """
        self.set_map  = set_map
        self.fun_map  = fun_map
        self.rel_map  = rel_map
        self.set_set  = set()
        self.fun_set  = set()
        self.rel_set  = set()
        self.fun_arg_map  = {}
        self.rel_arg_map  = {}
        self.fun_arg_set  = set()
        self.rel_arg_set  = set()
        return
    
    def process_aux_objs(self):
        """
        Process function and relation maps to extract argument sets
        """
        # Set of sets, functions and relations
        self.set_set = set(self.set_map.keys())
        self.fun_set = set(self.fun_map.keys())
        self.rel_set = set(self.rel_map.keys())
        # Map of functions and relations to their argument sets
        for k in self.fun_set:
            self.fun_arg_map[k] = extract_arg_set(k)
        for k in self.rel_set:
            self.rel_arg_map[k] = extract_arg_set(k)
        # Set of argument sets for functions and relations
        self.fun_arg_set = set(self.fun_arg_map.values())
        self.rel_arg_set = set(self.rel_arg_map.values())
        # Return
        return
    
    def get_placeholders( self, keyval : str) -> tuple[list]:
        """
        Get all placeholders in keyval
        """
        # Get all sets, funs and rels in keyval
        ph_sets = re.findall( rxconst.RX_SET_, keyval)
        ph_funs = re.findall( rxconst.RX_FUN_, keyval)
        ph_rels = re.findall( rxconst.RX_REL_, keyval)
        # Reconstruct full signatures from captured groups
        ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
        ph_rels_full = [f"{rel_name}[{arg_name}]" for rel_name, arg_name in ph_rels]
        # Check that sets, funs and rels in keyval are valid
        for ph in ph_sets:
            if ph not in self.set_set:
                print(f"Error: Set '{ph}' not found in signatures")
        for ph in ph_funs_full:
            if ph not in self.fun_set:
                print(f"Error: Function '{ph}' not found in signatures")
        for ph in ph_rels_full:
            if ph not in self.rel_set:
                print(f"Error: Relation '{ph}' not found in signatures")
        # Return lists
        return ph_sets, ph_funs_full, ph_rels_full

def load_placeholders( dir: str = 'newlang',
                       file: str = 'placeholders.json') -> placeholderData:
    # Load data
    placeholder_path = Path(__file__).parent / dir / file
    data = load_json_file(placeholder_path)
    ph_data = placeholderData()
    # Build set map
    for s in data.get('sets', []):
        if isinstance(s, dict) and len(s) == 1:
            set_name = list(s.keys())[0]
            values   = s[set_name]
            if not isvalid_set(values):
                print(f"Error: Set '{set_name}' is invalid: {values}")
            ph_data.set_map[set_name] = values
    # Build function map
    for f in data.get('functions', []):
        if isinstance(f, dict) and len(f) == 1:
            sig     = list(f.keys())[0]
            mapping = f[sig]
            if not isvalid_fun(sig, mapping, ph_data.set_map):
                print(f"Error: Function '{sig}' is invalid: {mapping}")
            ph_data.fun_map[sig] = mapping
    # Build relation map
    for r in data.get('relations', []):
        if isinstance(r, dict) and len(r) == 1:
            sig     = list(r.keys())[0]
            mapping = r[sig]
            if not isvalid_rel(sig, mapping, ph_data.set_map):
                print(f"Error: Relation '{sig}' is invalid: {mapping}")
            ph_data.rel_map[sig] = mapping
    # Process auxiliary objects
    ph_data.process_aux_objs()
    # Return placeholder data
    return ph_data
