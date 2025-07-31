#!/usr/bin/env python3
"""
Expansion utilities for placeholder substitution
"""

import itertools
import utilities as util

def expand_value( val : str | dict | list, ph_data : util.placeholderData) -> str | list:
    """
    Expand placeholders and function calls within a single value.
    
    Args:
        val: The value to expand (can be string, dict, list, or other types)
        ph_data: placeholderData object containing all placeholder information and set context in set_map
    
    Returns:
        Either a single expanded value or a list of expanded values (for relations)
    """
    if isinstance( val, str):
        # Find all placeholders in the string
        ph_rels = ph_data.get_placeholder_rels(val)
        # Check if any relations are present
        if ph_rels:
            # Handle relations (set-returning functions) by creating multiple expansions
            return _expand_with_relations(val, ph_data)
        else:
            # Handle regular functions and set placeholders
            return _expand_regular(val, ph_data)
    elif isinstance( val, dict):
        # Recursively expand dictionary values
        result = {}
        for k, v in val.items():
            result[k] = expand_value(v, ph_data)
        return result
    elif isinstance( val, list):
        # Recursively expand list elements
        result = []
        for v in val:
            result.append(expand_value(v, ph_data))
        return result
    # Return unchanged for other types
    return val

def _expand_regular( val : str, ph_data : util.placeholderData) -> str:
    """
    Expand regular functions and set placeholders (no relations).
    Returns a single expanded string.
    """
    result = val
    
    # Replace function calls first
    for func_sig, mapping in ph_data.fun_map.items():
        # Get the argument set name from the pre-computed map
        arg_set = ph_data.fun_arg_map[func_sig]
        if arg_set and arg_set in ph_data.set_map:
            arg_val = ph_data.set_map[arg_set]
            if arg_val in mapping:
                replacement = mapping[arg_val]
                result = util.replace_placeholder(result, replacement, func_sig)
    
    # Replace set placeholders
    for set_name, set_val in ph_data.set_map.items():
        result = util.replace_placeholder(result, set_val, set_name)
    
    return result

def _expand_with_relations( val : str, ph_data : util.placeholderData) -> list:
    """
    Expand values that contain relations (set-returning functions).
    Returns a list of expanded strings.
    """
    # Collect all possible expansions for each relation
    relation_expansions = []
    
    for rel_sig, mapping in ph_data.rel_map.items():
        # Get the argument set name from the pre-computed map
        arg_set = ph_data.rel_arg_map[rel_sig]
        if arg_set and arg_set in ph_data.set_map:
            arg_val = ph_data.set_map[arg_set]
            if arg_val in mapping:
                # Get the list of values returned by this relation
                relation_values = mapping[arg_val]
                relation_expansions.append((rel_sig, relation_values))
    
    if not relation_expansions:
        # No valid relations found, fall back to regular expansion
        return _expand_regular(val, ph_data)
    
    # Generate all combinations of relation expansions
    results = []
    rel_sigs = [exp[0] for exp in relation_expansions]
    rel_value_lists = [exp[1] for exp in relation_expansions]
    
    for combination in itertools.product(*rel_value_lists):
        expanded_val = val
        
        # Replace each relation with its value from the combination
        for rel_sig, replacement in zip(rel_sigs, combination):
            # For relations, we need to include the * prefix in the placeholder
            full_placeholder = f"*{rel_sig}"
            expanded_val = util.replace_placeholder(expanded_val, replacement, full_placeholder)
        
        # Also replace any remaining regular functions and set placeholders
        expanded_val = _expand_regular(expanded_val, ph_data)
        
        results.append(expanded_val)
    
    return results
