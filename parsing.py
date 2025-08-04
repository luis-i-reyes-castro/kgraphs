#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import data_structures_simplified as ds
import sys
import utilities as util
from collections import OrderedDict

def parse_components( data : OrderedDict,
                      phDB : ds.PlaceHolderDatabase) -> None :
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
                    fun_sig = key_funs[0]
                    fun_val = phDB.fun_map[fun_sig][element]
                    new_inner_key = phDB.replace( inner_key, fun_sig, fun_val)
                # Process inner val placeholders
                if val_funs :
                    fun_sig = val_funs[0]
                    fun_val = phDB.fun_map[fun_sig][element]
                    new_inner_val = phDB.replace( inner_val, fun_sig, fun_val)
                # Insert new key-value pair into inner dictionary
                result[new_key][new_inner_key] = new_inner_val
    
    return result

def parse_connections( data : OrderedDict,
                       phDB : ds.PlaceHolderDatabase) -> None :
    # Initialize results list
    result = []
    # Iterate through outer list
    for comp_pair in data :
        # Copy components
        comp_1 = comp_pair[0]
        comp_2 = comp_pair[1]
        # Get placehbolder sets
        comp_1_sets = phDB.get_placeholder_sets(comp_1)
        comp_2_sets = phDB.get_placeholder_sets(comp_2)
        # If component 1 has at least one set then process first one
        if comp_1_sets :
            set = comp_1_sets[0]
            # Iterate through elements of the set
            for element in phDB.set_map[set] :
                # Initialize component pair
                new_comp_1 = phDB.replace( comp_1, set, element)
                new_comp_2 = comp_2
                # Get component 2 placeholder functions and relations
                comp_2_funs = phDB.get_placeholder_funs(comp_2)
                comp_2_rels = phDB.get_placeholder_rels(comp_2)
                # If component 2 has at least one function then process first one
                if comp_2_funs :
                    fun_sig = comp_2_funs[0]
                    fun_val = phDB.fun_map[fun_sig][element]
                    new_comp_2 = phDB.replace( comp_2, fun_sig, fun_val)
                # If component 2 has at least one relation then process first one
                elif comp_2_rels :
                    rel_sig = comp_2_rels[0]
                    rel_val = phDB.rel_map[rel_sig][element]
                    for rel_element in rel_val :
                        new_comp_2 = phDB.replace_relation( comp_2, rel_sig, rel_element)
                        result.append( [ new_comp_1, new_comp_2] )
                    continue
                # Insert new component pair into results list
                result.append( [ new_comp_1, new_comp_2] )
        # If component 2 has at least one set then process first one
        elif comp_2_sets :
            set = comp_2_sets[0]
            # Iterate through elements of the set
            for element in phDB.set_map[set] :
                # Initialize component pair
                new_comp_1 = comp_1
                new_comp_2 = phDB.replace( comp_2, set, element)
                # Insert new component pair into results list
                result.append( [ new_comp_1, new_comp_2] )
        # If no sets then insert original component pair into results list
        else :
            result.append( comp_pair )
    
    return result

if __name__ == "__main__" :
    
    if len(sys.argv) < 2:
        print("Usage: python parsing.py <json_file>")
        exit(1)
    
    placeholderDB = ds.load_placeholders()
    
    json_file = sys.argv[1]
    file_data = util.load_json_file(json_file)
    util.print_sep()
    util.print_recursively(file_data)
    
    util.print_sep()
    result = parse_connections( file_data, placeholderDB)
    util.print_recursively(result)
    util.print_sep()
