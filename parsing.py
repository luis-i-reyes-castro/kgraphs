#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import utilities as util
import data_structures_simplified as ds
from collections import OrderedDict

def parse_components( data : OrderedDict,
                      placeholderDB : ds.PlaceHolderDatabase,
                      verbose = False) -> None :
    
    result = OrderedDict()

    if verbose :
        print('RUNNING: parse_components()')
        print('Parsing Outer Dict...')
    for key, inner_dict in data.items() :
        
        if verbose :
            util.print_ind(f'Key: {key}')
        
        key_sets = placeholderDB.get_placeholder_sets(key)
        # Key has no placeholder set
        if not key_sets :
            result[key] = dict(inner_dict)
            if verbose :
                util.print_ind( f'No set placeholders found', 1)
        # Key has one placeholder set
        else :
            set = key_sets[0]
            if verbose :
                util.print_ind( f'Set placeholder: {set}', 1)
            
            for element in placeholderDB.set_map[set] :
                if verbose :
                    util.print_ind( f'Processing element: {element}', 2)
                
                new_key = util.replace_placeholder( key, set, element)
                result[new_key] = {}
                if verbose :
                    util.print_ind( f'New key: {new_key}', 2)
                
                if verbose :
                    util.print_ind( f'Parsing Inner Dict...', 2)
                
                for id_key, id_val in inner_dict.items() :
                    
                    new_id_key = id_key
                    key_funs   = placeholderDB.get_placeholder_funs(id_key)
                    if verbose :
                        util.print_ind( f'Key: {id_key}', 3)
                    if key_funs :
                        fun = key_funs[0]
                        fun_val = placeholderDB.fun_map[fun][element]
                        if verbose :
                            util.print_ind( f'Function placeholder: {fun} = {fun_val}', 4)
                        new_id_key = util.replace_placeholder( id_key, fun, fun_val)
                        if verbose :
                            util.print_ind( f'New key: {new_id_key}', 5)
                    else :
                        if verbose :
                            util.print_ind( f'No function placeholders found', 4)
                    
                    new_id_val = id_val
                    val_funs   = placeholderDB.get_placeholder_funs(id_val)
                    if verbose :
                        util.print_ind( f'Val: {id_val}', 3)
                    if val_funs :
                        fun = val_funs[0]
                        fun_val = placeholderDB.fun_map[fun][element]
                        if verbose :
                            util.print_ind( f'Function placeholder: {fun} = {fun_val}', 4)
                        new_id_val = util.replace_placeholder( id_val, fun, fun_val)
                        if verbose :
                            util.print_ind( f'New val: {new_id_val}', 5)
                    else :
                        if verbose :
                            util.print_ind( f'No function placeholders found', 4)
                    
                    result[new_key][new_id_key] = new_id_val
    
    return result

if __name__ == "__main__" :

    placeholderDB = ds.load_placeholders()
    
    component_data = util.load_json_file('newlang/components_spraying.json')
    util.print_sep()
    util.print_recursively(component_data)
    
    result = parse_components( component_data, placeholderDB, verbose = False)
    util.print_sep()
    util.print_recursively(result)
    util.print_sep()
