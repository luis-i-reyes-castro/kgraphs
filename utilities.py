#!/usr/bin/env python3
"""
Utilities for placeholder substitution
"""

import regex_constants as rxconst
from collections import OrderedDict
from json import load
from re import search

def load_json_file( filepath : str) -> OrderedDict:
    """
    Load JSON file as OrderedDict
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return load( f, object_pairs_hook = OrderedDict)

def print_recursively( data : str | dict | list, indent = 0) -> None:
    space = '  ' * indent
    if isinstance( data, str):
        print(f"{space}{data}")
    elif isinstance( data, dict):
        print(f"{space}{'{'}")
        for key, value in data.items():
            print(f"{space}{key}:")
            print_recursively( value, indent + 1)
        print(f"{space}{'}'}")
    elif isinstance( data, list):
        print(f"{space}{'['}")
        for item in data:
            print_recursively( item, indent + 1)
        print(f"{space}{']'}")
    return

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
    match = search( rxconst.RX_ARG, sig)
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
    match = search( rxconst.RX_ARG, sig)
    return match.group(1) if match else None

def replace_placeholder( val_orig : str, val_new : str, sig : str) -> str:
    """
    Replace a placeholder with a new value
    """
    return val_orig.replace( f'({sig})', val_new)
