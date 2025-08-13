#!/usr/bin/env python3
"""
Functions for loading data after expansion
"""

from utilities_io import load_json_files_starting_with

def load_domain_knowledge( directory : str) -> dict :
    result = {}
    result['messages']   = load_json_files_starting_with( directory, 'messages_')
    result['diagnoses']  = load_json_files_starting_with( directory, 'diagnoses_')
    result['components'] = load_json_files_starting_with( directory, 'components_')
    result['problems']   = load_json_files_starting_with( directory, 'problems_')
    return result
