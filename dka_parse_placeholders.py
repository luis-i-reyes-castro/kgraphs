#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import os
import shutil
from abc_project_vars import DIR_DKA
from abc_project_vars import DIR_DKB
from collections import OrderedDict
from dka_data_structures import PlaceHolderDatabase
from dka_data_structures import contains_placeholders
from dka_data_structures import load_placeholders
from utilities_io import ensure_dir
from utilities_io import load_json_file
from utilities_io import save_to_json_file
from utilities_printing import print_ind

def parse_dict( data : OrderedDict, phDB : PlaceHolderDatabase) -> OrderedDict :
    
    result = OrderedDict()
    
    for outer_key, inner_data in data.items() :
        outer_key_set = phDB.get_first_placeholder( outer_key, 'set')
        if outer_key_set and ( outer_key_set in phDB.set_map ) :
            for element in phDB.set_map[outer_key_set] :
                new_outer_key         = phDB.apply_ph( outer_key, outer_key_set, element)
                result[new_outer_key] = phDB.apply_funs( inner_data, element)
        else :
            result[outer_key] = OrderedDict(inner_data)
    
    return result

def parse_connections( data : list, phDB : PlaceHolderDatabase) -> list[list] :
    
    result = []

    for inner_list in data :
        comp_1 = inner_list[0]
        comp_2 = inner_list[1]
        
        set_ph = phDB.get_first_placeholder( comp_1, 'set')
        if set_ph and ( set_ph in phDB.set_map ) :
            for set_element in phDB.set_map[set_ph] :
                new_comp_1 = phDB.apply_ph( comp_1, set_ph, set_element)
                new_comp_2 = phDB.apply_funs( comp_2, set_element)
                result.append( [ new_comp_1, new_comp_2] )
        
        else :
            set_ph = phDB.get_first_placeholder( comp_2, 'set')
            if set_ph and ( set_ph in phDB.set_map ) :
                for set_element in phDB.set_map[set_ph] :
                    new_comp_1 = comp_1
                    new_comp_2 = phDB.apply_ph( comp_2, set_ph, set_element)
                    result.append( [ new_comp_1, new_comp_2] )
            
            else :
                result.append(inner_list)
    
    return result

def parse_messages( data : OrderedDict, phDB : PlaceHolderDatabase) -> OrderedDict :
    
    result = parse_dict( data, phDB)
    
    for message_key, message_data in data.items() :
        if str(message_key).startswith('error_') :
            causes = message_data['causes']
            causes['components'] = phDB.extend_list(causes['components'])
            causes['problems']   = phDB.extend_list(causes['problems'])
            causes['signals']    = phDB.extend_list(causes['signals'])
    
    return result

def parse_signals( data : list,
                   phDB : PlaceHolderDatabase) -> list[OrderedDict] :
    
    result = []

    for inner_dict in data :
        list_signals = inner_dict['signals']
        list_path    = inner_dict['path']
        signals_set  = phDB.get_first_placeholder( list_signals, 'set')
        
        if signals_set and ( signals_set in phDB.set_map ) :
            for set_element in phDB.set_map[signals_set] :
                new_inner_dict = OrderedDict()
                new_inner_dict['signals'] = phDB.apply_ph( list_signals,
                                                           signals_set,
                                                           set_element)
                new_inner_dict['path']    = phDB.apply_funs( list_path, set_element)
                result.append(new_inner_dict)
        
        else :
            result.append(OrderedDict(inner_dict))
    
    return result

if __name__ == "__main__" :
    
    dir_input  = DIR_DKA
    dir_output = DIR_DKB

    print_ind(f'Expanding domain knowledge from: {dir_input}')
    ensure_dir(dir_output)
    print_ind(f'Saving files to: {dir_output}')

    batch      = ( 'components_', 'connections', 'messages_', 'problems_', 'signals_')
    exceptions = ( 'placeholders',)

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
        if not filename.startswith(batch) :
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
        if filename.startswith(('components_','problems_')) :
            parsed_data = parse_dict( file_data, placeholderDB)
        elif filename.startswith('connections') :
            parsed_data = parse_connections( file_data, placeholderDB)
        elif filename.startswith('messages_') :
            parsed_data = parse_messages( file_data, placeholderDB)
        elif filename.startswith('signals_') :
            parsed_data = parse_signals( file_data, placeholderDB)
        else :
            raise ValueError( f'Unknown batch: {filename}')
        
        # Write the parsed data as JSON to the output directory
        save_to_json_file( parsed_data, path_output)
        print_ind( f'File data expanded.', 1)
        
        # Warn of leftover placeholders
        if contains_placeholders(parsed_data) :
            print_ind(f'⚠️ WARNING: Post-processing found leftover placeholders!')
