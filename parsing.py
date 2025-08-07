#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import data_structures as ds
import parsing_utilities as pu
from collections import OrderedDict

def parse_dict_of_dicts( data : OrderedDict,
                         phDB : ds.PlaceHolderDatabase) -> OrderedDict :
    # Initialize result dictionary
    result = OrderedDict()
    # Iterate through outer dictionary key-val pairs
    for outer_key, inner_dict in data.items() :
        outer_key_set = phDB.get_first_placeholder( outer_key, 'set')
        # Key has no sets, copy inner dict and continue.
        if not outer_key_set :
            result[outer_key] = OrderedDict(inner_dict)
            continue
        # Key has a set so iterate thorugh elements of the set
        for element in phDB.set_map[outer_key_set] :
            # Replace placeholder set in key and initialize inner dictionary
            new_key = phDB.replace( outer_key, outer_key_set, element)
            result[new_key] = OrderedDict()
            # Iterate through inner dictionary key-value pairs
            for inner_key, inner_val in inner_dict.items() :
                # Copy key and value
                new_inner_key = inner_key
                new_inner_val = inner_val
                # Get function placeholders in inner key and value
                inner_key_fun = phDB.get_first_placeholder( inner_key, 'fun')
                inner_val_fun = phDB.get_first_placeholder( inner_val, 'fun')
                # Process inner key placeholders
                if inner_key_fun :
                    fun_val = phDB.fun_map[inner_key_fun][element]
                    new_inner_key = phDB.replace( inner_key, inner_key_fun, fun_val)
                # Process inner val placeholders
                if inner_val_fun :
                    fun_val = phDB.fun_map[inner_val_fun][element]
                    new_inner_val = phDB.replace( inner_val, inner_val_fun, fun_val)
                # Insert new key-value pair into inner dictionary
                result[new_key][new_inner_key] = new_inner_val
    # The grand finale
    return result

def parse_list_of_pairs( data : OrderedDict,
                         phDB : ds.PlaceHolderDatabase) -> list[list[str]] :
    # Initialize results list
    result = []
    # Iterate through outer list
    for comp_pair in data :
        # Copy components
        comp_1 = comp_pair[0]
        comp_2 = comp_pair[1]
        # Get placehbolder sets
        comp_1_set = phDB.get_first_placeholder( comp_1, 'set')
        comp_2_set = phDB.get_first_placeholder( comp_2, 'set')
        # If component 1 has at least one set then process first one
        if comp_1_set :
            # Iterate through elements of the set
            for set_element in phDB.set_map[comp_1_set] :
                # Initialize component pair
                new_comp_1 = phDB.replace( comp_1, comp_1_set, set_element)
                new_comp_2 = comp_2
                # Get component 2 placeholder functions and relations
                comp_2_fun = phDB.get_first_placeholder( comp_2, 'fun')
                comp_2_rel = phDB.get_first_placeholder( comp_2, 'rel')
                # If component 2 has at least one function then process first one
                if comp_2_fun :
                    fun_val    = phDB.fun_map[comp_2_fun][set_element]
                    new_comp_2 = phDB.replace( comp_2, comp_2_fun, fun_val)
                # If component 2 has at least one relation then process first one
                elif comp_2_rel :
                    rel_val = phDB.rel_map[comp_2_rel][set_element]
                    for rel_element in rel_val :
                        new_comp_2 = phDB.replace_relation( comp_2, comp_2_rel, rel_element)
                        result.append( [ new_comp_1, new_comp_2] )
                    continue
                # Insert new component pair into results list
                result.append( [ new_comp_1, new_comp_2] )
        # If component 2 has at least one set then process first one
        elif comp_2_set :
            # Iterate through elements of the set
            for set_element in phDB.set_map[comp_2_set] :
                # Initialize component pair
                new_comp_1 = comp_1
                new_comp_2 = phDB.replace( comp_2, comp_2_set, set_element)
                # Insert new component pair into results list
                result.append( [ new_comp_1, new_comp_2] )
        # If no sets then insert original component pair into results list
        else :
            result.append( comp_pair )
    # The grand finale
    return result

def parse_diagnoses( data : OrderedDict,
                     phDB : ds.PlaceHolderDatabase) -> OrderedDict :
    # Initialize results dict
    result = OrderedDict()
    # Iterate through outer list
    for item in data :
        # Retrieve error group and causes
        group_errors = item['group_errors']
        group_causes = item['group_causes']
        # Get error group placeholder set
        group_set = phDB.get_first_placeholder( group_errors, 'set')
        # If no sets then make one key for each error, insert it into the result,
        # and copy the causes without function replacement
        if not group_set :
            # Iterate through error strings in list
            for error in group_errors :
                # Initialize resulting causes list
                result[error] = []
                # Iterate through cause dictionaries in list
                for cause in group_causes :
                    # Check if cause has valid keys
                    if not pu.has_valid_cause_keys(cause):
                        raise ValueError( f'Invalid cause keys: {cause}')
                    # If the cause is a component
                    comp_str = 'component'
                    if comp_str in cause.keys() :
                        # If the component has placeholder sets
                        comp_val = cause[comp_str]
                        comp_set = phDB.get_first_placeholder( comp_val, 'set')
                        if comp_set :
                            # Iterate through elements of the set
                            for set_element in phDB.set_map[comp_set] :
                                # Copy the cause dictionary
                                inner_result = OrderedDict(cause)
                                # Replace placeholder
                                new_comp_val = \
                                phDB.replace( comp_val, comp_set, set_element)
                                # Insert new component value into cause dict
                                inner_result[comp_str] = new_comp_val
                                # Insert dict into results list
                                result[error].append(inner_result)
                            # Move on to next cause
                            continue
                    # Component has no set placeholders, so just copy cause dict.
                    result[error].append(OrderedDict(cause))
            continue
        # There is a set, so iterate through errors and elements of the set.
        for error in group_errors :
            for set_element in phDB.set_map[group_set] :
                # Result outer key is error with placeholder set replaced
                outer_key = phDB.replace( error, group_set, set_element)
                result[outer_key] = []
                # Iterate through list of error causes. Each cause is a dict.
                for cause in group_causes :
                    # Check if cause has valid keys
                    if not pu.has_valid_cause_keys(cause):
                        raise ValueError( f'Invalid cause keys: {cause}')
                    # Initialize inner result dict
                    inner_result = OrderedDict()
                    # Iterate through cause key-val pairs
                    for cause_key, cause_val in cause.items():
                        # Key is unchanged; val is initialized.
                        new_cause_val = cause_val
                        # If val has a placeholder function then apply.
                        val_fun = phDB.get_first_placeholder( cause_val, 'fun')
                        if val_fun :
                            fun_output    = phDB.fun_map[val_fun][set_element]
                            new_cause_val = phDB.replace( cause_val, val_fun, fun_output)
                        # Populate inner result dict
                        inner_result[cause_key] = new_cause_val
                    # Populate list of causes
                    result[outer_key].append(inner_result)
    # The grand finale
    return result
