#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import data_structures_simplified as ds
import sys
import utilities as util
from collections import OrderedDict

def parse_components( data : OrderedDict,
                      phDB : ds.PlaceHolderDatabase,
                      verbose = False) -> None :
    # Initialize result dictionary
    result = OrderedDict()
    # Iterate through outer dictionary key-val pairs
    for key, inner_dict in data.items() :
        key_sets = phDB.get_placeholder_sets(key)
        # Key has no sets, copy inner dict and continue.
        if not key_sets :
            result[key] = OrderedDict(inner_dict)
            continue
        # Key has at least one set, process the first only.
        set = key_sets[0]
        # Iterate thorugh elements of the set
        for element in phDB.set_map[set] :
            # Replace placeholder set in key and initialize inner dictionary
            new_key = phDB.replace( key, set, element)
            result[new_key] = OrderedDict()
            # Iterate through inner dictionary key-value pairs
            for inner_key, inner_val in inner_dict.items() :
                # Copy key and value
                new_inner_key = inner_key
                new_inner_val = inner_val
                # Get function placeholders in inner key and value
                key_funs = phDB.get_placeholder_funs(inner_key)
                val_funs = phDB.get_placeholder_funs(inner_val)
                # Process inner key placeholders
                if key_funs :
                    fun_sign = key_funs[0]
                    fun_val = phDB.fun_map[fun_sign][element]
                    new_inner_key = phDB.replace( inner_key, fun_sign, fun_val)
                # Process inner val placeholders
                if val_funs :
                    fun_sign = val_funs[0]
                    fun_val = phDB.fun_map[fun_sign][element]
                    new_inner_val = phDB.replace( inner_val, fun_sign, fun_val)
                # Insert new key-value pair into inner dictionary
                result[new_key][new_inner_key] = new_inner_val
    
    return result

if __name__ == "__main__" :
    
    if len(sys.argv) < 2:
        print("Usage: python parsing.py <json_file>")
        exit(1)
    
    placeholderDB = ds.load_placeholders()
    
    json_file      = sys.argv[1]
    component_data = util.load_json_file(json_file)
    util.print_sep()
    util.print_recursively(component_data)
    
    result = parse_components( component_data, placeholderDB, verbose = False)
    util.print_sep()
    util.print_recursively(result)
    util.print_sep()
