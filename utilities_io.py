#!/usr/bin/env python3
"""
Utilities for Input/Output (IO) Operations
"""

from collections import OrderedDict
from glob import glob
from json import dump
from json import load
from json import loads
from typing import Any

def load_file_as_string( filepath : str) -> str :
    """
    Load JSON file as string
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return f.read()

def load_json_file( filepath : str) -> Any :
    """
    Load JSON file as OrderedDict
    """
    with open( filepath, 'r', encoding='utf-8') as f:
        return load( f, object_pairs_hook = OrderedDict)

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

def load_json_string( data : str) -> Any :
    """
    Load JSON from a string, handling markdown code blocks if present.
    """
    # Strip whitespace
    data  = data.strip()
    # Check if the data is wrapped in markdown code blocks
    cond1 = data.startswith("```json") and data.endswith("```")
    cond2 = data.startswith("```") and data.endswith("```")
    # If the data is wrapped in markdown code blocks, extract the JSON content.
    if cond1 or cond2 :
        # Split the data into lines
        lines = data.split('\n')
        # Remove first and last lines
        json_lines = lines[1:-1]
        # Reassemble the data
        data = '\n'.join(json_lines)
    # Load the JSON
    return loads( data, object_pairs_hook = OrderedDict)

def save_json_file( filepath : str, data : Any) -> None :
    """
    Save JSON file as OrderedDict
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        dump(data, f, indent=2, ensure_ascii=False)
    return
