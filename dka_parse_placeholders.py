#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import os
import shutil
from abc_project_vars import DIR_DKNOWLEDGE_A
from abc_project_vars import DIR_DKNOWLEDGE_B
from collections import OrderedDict
from dka_data_structures import load_placeholders
from dka_data_structures import PlaceHolderDatabase
from utilities_io import ensure_dir
from utilities_io import load_json_file
from utilities_io import save_to_json_file
from utilities_printing import print_ind

def parse_dict_of_dicts( data : OrderedDict,
                         phDB : PlaceHolderDatabase) -> OrderedDict :
    
    result = OrderedDict()
    
    for outer_key, inner_dict in data.items() :
        outer_key_set = phDB.get_first_placeholder( outer_key, 'set')
        if outer_key_set :
            for element in phDB.set_map[outer_key_set] :
                new_outer_key         = phDB.apply_ph( outer_key, outer_key_set, element)
                result[new_outer_key] = phDB.eval_apply_funs( inner_dict, element)
        else :
            result[outer_key] = OrderedDict(inner_dict)
    
    return result

def parse_list_of_lists( data : list,
                         phDB : PlaceHolderDatabase) -> list[list] :
    
    result = []

    for inner_list in data :
        
        set_index = None
        set_ph    = ''
        for i, item in enumerate(inner_list) :
            item_set = phDB.get_first_placeholder( item, 'set')
            if item_set:
                set_index = i
                set_ph    = item_set
                break
        
        if set_index :
            for set_element in phDB.set_map[set_ph] :
                
                new_inner_list = list(inner_list) 
                new_inner_list[set_index] = \
                phDB.apply_ph(inner_list[set_index], set_ph, set_element)

                for j, _ in enumerate(new_inner_list) :
                    if j != set_index :
                        new_inner_list[j] = \
                        phDB.eval_apply_funs(new_inner_list[j], set_element)
                
                result.append(new_inner_list)
        
        else:
            result.append(inner_list)
    
    return result

def parse_signals( data : list,
                   phDB : PlaceHolderDatabase) -> list[OrderedDict] :
    
    result = []

    for inner_dict in data :
        list_signals = inner_dict['signals']
        list_path    = inner_dict['path']
        signals_set  = phDB.get_first_placeholder( list_signals, 'set')
        
        if signals_set :
            for set_element in phDB.set_map[signals_set] :
                new_inner_dict = OrderedDict()
                new_inner_dict['signals'] = phDB.apply_ph( list_signals,
                                                           signals_set,
                                                           set_element)
                new_inner_dict['path']    = phDB.eval_apply_funs( list_path,
                                                                  set_element)
                result.append(new_inner_dict)
        
        else :
            result.append(OrderedDict(inner_dict))
    
    return result

def parse_messages( data : OrderedDict, phDB : PlaceHolderDatabase) -> OrderedDict :
    
    result = parse_dict_of_dicts( data, phDB)
    
    for problem_key, problem_data in data.items() :
        # TODO: Expand sets in lists: components, problems, signals
        pass
    
    return result

if __name__ == "__main__" :
    
    dir_input  = DIR_DKNOWLEDGE_A
    dir_output = DIR_DKNOWLEDGE_B

    print_ind(f'Expanding domain knowledge from: {dir_input}')
    ensure_dir(dir_output)
    print_ind(f'Saving files to: {dir_output}')

    batch_dicts = ( 'components_', 'problems_')
    batch_conns = ( 'connections',)
    batch_signs = ( 'signals_',)
    batch_msgs  = ( 'messages_',)
    exceptions    = ( 'placeholders',)
    batch_full = batch_dicts + batch_conns + batch_signs + batch_msgs

    # Load the placeholder database
    path_placeholders = os.path.join( dir_input, 'placeholders.json')
    placeholderDB     = load_placeholders(path_placeholders)
    
    # List all files in the input directory
    dir_input_filenames = os.listdir(dir_input)
    dir_input_filenames.sort()
    
    for filename in dir_input_filenames :
        path_input  = os.path.join( dir_input, filename)
        path_output = os.path.join( dir_output, filename)
        print_ind(f'Processing file: {path_input}')
        
        # Root out non-json files
        if not filename.endswith('.json') :
            print_ind( f'File is not JSON. Skipped.', 1)
            continue
        
        # If file is not in batch and not in exceptions then copy
        if not filename.startswith(batch_full) :
            if not filename.startswith(exceptions) :
                shutil.copy (path_input, path_output)
                print_ind( f'File is neither expandable nor in exceptions. Copied.', 1)
            else :
                print_ind( f'File is in exceptions. Skipped.', 1)
            continue
        
        # Load the JSON file
        file_data   = load_json_file(path_input)
        parsed_data = None
        
        # Parse according to batch type
        if filename.startswith(batch_dicts) :
            parsed_data = parse_dict_of_dicts( file_data, placeholderDB)
        elif filename.startswith(batch_conns) :
            parsed_data = parse_list_of_lists( file_data, placeholderDB)
        elif filename.startswith(batch_signs) :
            parsed_data = parse_signals( file_data, placeholderDB)
        elif filename.startswith(batch_msgs) :
            parsed_data = parse_messages( file_data, placeholderDB)
        else :
            raise ValueError( f'Unknown batch: {filename}')
        
        # Write the parsed data as JSON to the output directory
        save_to_json_file( parsed_data, path_output)
        print_ind( f'File data expanded.', 1)
