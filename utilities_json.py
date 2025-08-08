#!/usr/bin/env python3
"""
Utilities for placeholder substitution
"""

from collections import OrderedDict
from glob import glob
from json import dump
from json import load
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

def load_json_files_starting_with( directory : str, prefix : str) -> dict :
    result = {}
    files  = glob(f'{directory}/{prefix}*.json')
    for file_path in files :
        try :
            file_contents = load_json_file(file_path)
            result.update(file_contents)
        except FileNotFoundError as e :
            print(f"❌ Error: Could not find file {e.filename}")
            continue
    return result

def save_json_file( filepath : str, data : Any) -> None :
    """
    Save JSON file as OrderedDict
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        dump(data, f, indent=2, ensure_ascii=False)
    return
