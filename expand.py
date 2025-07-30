#!/usr/bin/env python3
"""
Expansion utilities for placeholder substitution
"""

import itertools
import utilities as util

def expand_value( val : str | dict | list,
                  set_context : dict,
                  func_map : dict,
                  rel_map : dict) -> str | list:
    """
    Expand placeholders and function calls within a single value.
    
    Args:
        val: The value to expand (can be string, dict, list, or other types)
        set_context: Dictionary mapping set names to their current values (e.g., {"SIDE": "l"})
        func_map: Dictionary mapping function signatures to their mappings
        rel_map: Dictionary mapping relation signatures to their mappings
    
    Returns:
        Either a single expanded value or a list of expanded values (for relations)
    """
    if isinstance( val, str):
        # Get all signatures
        signatures = util.get_signatures( set_context, func_map, rel_map)
        # Find all placeholders in the string
        ph_sets, ph_funs, ph_rels = util.get_placeholders( val, signatures)
        # Check if any relations are present
        if ph_rels:
            # Handle relations (set-returning functions) by creating multiple expansions
            return _expand_with_relations( val, set_context, func_map, rel_map)
        else:
            # Handle regular functions and set placeholders
            return _expand_regular( val, set_context, func_map)
    
    elif isinstance( val, dict):
        # Recursively expand dictionary values
        result = {}
        for k, v in val.items():
            result[k] = expand_value( v, set_context, func_map, rel_map)
        return result
    
    elif isinstance( val, list):
        # Recursively expand list elements
        result = []
        for v in val:
            result.append( expand_value( v, set_context, func_map, rel_map) )
        return result
    
    # Return unchanged for other types
    return val

def _expand_regular( val : str,
                     set_context : dict,
                     func_map : dict) -> str:
    """
    Expand regular functions and set placeholders (no relations).
    Returns a single expanded string.
    """
    result = val
    
    # Replace function calls first
    for func_sig, mapping in func_map.items():
        # Extract the argument set name from the function signature
        arg_set = util.extract_arg_set(func_sig)
        if arg_set and arg_set in set_context:
            arg_val = set_context[arg_set]
            if arg_val in mapping:
                replacement = mapping[arg_val]
                result = util.replace_placeholder(result, replacement, func_sig)
    
    # Replace set placeholders
    for set_name, set_val in set_context.items():
        result = util.replace_placeholder(result, set_val, set_name)
    
    return result

def _expand_with_relations(val : str,
                           set_context : dict,
                           func_map : dict,
                           rel_map : dict) -> list:
    """
    Expand values that contain relations (set-returning functions).
    Returns a list of expanded strings.
    """
    # Collect all possible expansions for each relation
    relation_expansions = []
    
    for rel_sig, mapping in rel_map.items():
        # Extract the argument set name from the relation signature
        arg_set = util.extract_arg_set(rel_sig)
        if arg_set and arg_set in set_context:
            arg_val = set_context[arg_set]
            if arg_val in mapping:
                # Get the list of values returned by this relation
                relation_values = mapping[arg_val]
                relation_expansions.append((rel_sig, relation_values))
    
    if not relation_expansions:
        # No valid relations found, fall back to regular expansion
        return _expand_regular(val, set_context, func_map)
    
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
        expanded_val = _expand_regular(expanded_val, set_context, func_map)
        
        results.append(expanded_val)
    
    return results
