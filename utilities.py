#!/usr/bin/env python3
"""
Utilities for placeholder substitution
"""

from collections import OrderedDict
from json import load
from json import dump
from typing import Any

def load_json_file( filepath : str) -> Any :
    """
    Load JSON file as OrderedDict
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return load( f, object_pairs_hook = OrderedDict)

def load_json_file_as_string( filepath : str) -> str :
    """
    Load JSON file as string
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_json_file( filepath : str, data : Any) -> None :
    """
    Save JSON file as OrderedDict
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        dump(data, f, indent=2, ensure_ascii=False)
    return

def print_sep( width : int = 80) -> None :
    print( '-' * width )
    return

def print_ind( arg : str, indent = 0) -> None :
    space = '  ' * indent
    print(f'{space}{arg}')
    return

def print_recursively( data : str | dict | list | tuple, indent = 0) -> None :
    
    if isinstance( data, str):
        print_ind( data, indent)
    
    elif isinstance( data, dict):
        print_ind( '{', indent)
        for key, value in data.items():
            print_ind( f'{key}:', indent)
            print_recursively( value, indent + 1)
        print_ind( '}', indent)
    
    elif isinstance( data, list):
        print_ind( '[', indent)
        for item in data:
            print_recursively( item, indent + 1)
        print_ind( ']', indent)
    
    elif isinstance( data, tuple):
        print_ind( '(', indent)
        for item in data:
            print_recursively( item, indent + 1)
        print_ind( ')', indent)

    else :
        raise ValueError(f'Invalid data type: {type(data)}')
    
    return
