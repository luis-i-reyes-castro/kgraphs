#!/usr/bin/env python3
"""
Utilities for Input/Output (IO) Operations
"""

from collections import OrderedDict
from glob import glob
from json import dump
from json import load
from json import loads
from pathlib import Path
from typing import Any

def ensure_dir( dir_name : str) -> None :
    """
    Ensure directory exists.
    """
    Path(dir_name).mkdir( parents = True, exist_ok = True)
    return

def exists_file( filepath : str) -> bool :
    """
    Check if a file exists.
    """
    return Path(filepath).exists()

def load_file_as_string( filepath : str) -> str :
    """
    Load JSON file as string
    """
    with open( filepath, 'r', encoding = 'utf-8') as f :
        return f.read()

def load_json_file( filepath : str) -> Any :
    """
    Load JSON file as OrderedDict
    """
    with open( filepath, 'r', encoding = 'utf-8') as f :
        return load( f, object_pairs_hook = OrderedDict)

def load_json_files_starting_with( directory : str, prefix : str) -> dict :
    """
    Load all JSON files in a directory starting with a given prefix
    """
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
    data = remove_markdown_header_footer( data, 'json')
    return loads( data, object_pairs_hook = OrderedDict)

def remove_markdown_header_footer( data : str, data_type) -> str :
    """
    Remove markdown header and footer
    """
    data  = data.strip()
    cond1 = data.startswith( ( "```", "```" + data_type) )
    cond2 = data.endswith( "```" )
    if cond1 or cond2 :
        lines = data.split('\n')
        if cond1 :
            lines = lines[1:]
        if cond2 :
            lines = lines[:-1]
        data = '\n'.join(lines)
    return data

def save_data_to_json_file( data : Any, filepath : str) -> None :
    """
    Save data to JSON file
    """
    with open( filepath, 'w', encoding = 'utf-8') as f :
        dump( data, f, indent = 4, ensure_ascii = False)
    return
