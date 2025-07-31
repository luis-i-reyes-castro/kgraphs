#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import regex_constants as rxconst
import utilities as util
from pathlib import Path
from re import findall

class PlaceHolderData:
    """
    Convenience object for storing all placeholder data
    """
    
    def __init__(self, set_map : dict = {}, fun_map : dict = {}, rel_map : dict = {}):
        """
        Initialize placeholder data
        """
        self.set_map  = set_map
        self.fun_map  = fun_map
        self.rel_map  = rel_map
        self.set_set  = set()
        self.fun_set  = set()
        self.rel_set  = set()
        self.fun_arg_map  = {}
        self.rel_arg_map  = {}
        self.fun_arg_set  = set()
        self.rel_arg_set  = set()
        return
    
    def process_aux_objs(self):
        """
        Process function and relation maps to extract argument sets
        """
        # Set of sets, functions and relations
        self.set_set = set(self.set_map.keys())
        self.fun_set = set(self.fun_map.keys())
        self.rel_set = set(self.rel_map.keys())
        # Map of functions and relations to their argument sets
        for k in self.fun_set:
            self.fun_arg_map[k] = util.extract_arg_set(k)
        for k in self.rel_set:
            self.rel_arg_map[k] = util.extract_arg_set(k)
        # Set of argument sets for functions and relations
        self.fun_arg_set = set(self.fun_arg_map.values())
        self.rel_arg_set = set(self.rel_arg_map.values())
        # Return
        return
    
    def get_placeholder_sets( self, keyval : str) -> list:
        """
        Get all placeholder sets in keyval
        """
        ph_sets = findall( rxconst.RX_SET_, keyval)
        for ph in ph_sets:
            if ph not in self.set_set:
                print(f"Error: Set '{ph}' not found in signatures")
        return ph_sets
    
    def get_placeholder_funs( self, keyval : str) -> list:
        """
        Get all placeholder functions in keyval
        """
        ph_funs = findall( rxconst.RX_FUN_, keyval)
        ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
        for ph in ph_funs_full:
            if ph not in self.fun_set:
                print(f"Error: Function '{ph}' not found in signatures")
        return ph_funs_full
    
    def get_placeholder_rels( self, keyval : str) -> list:
        """
        Get all placeholder relations in keyval
        """
        ph_rels = findall( rxconst.RX_REL_, keyval)
        ph_rels_full = [f"{rel_name}[{arg_name}]" for rel_name, arg_name in ph_rels]
        for ph in ph_rels_full:
            if ph not in self.rel_set:
                print(f"Error: Relation '{ph}' not found in signatures")
        return ph_rels_full

    def get_placeholders( self, keyval : str) -> tuple[list]:
        """
        Get all placeholders in keyval
        """
        ph_sets = self.get_placeholder_sets(keyval)
        ph_funs = self.get_placeholder_funs(keyval)
        ph_rels = self.get_placeholder_rels(keyval)
        return ph_sets, ph_funs, ph_rels

def load_placeholders( dir: str = 'newlang',
                       file: str = 'placeholders.json') -> PlaceHolderData:
    # Load data
    placeholder_path = Path(__file__).parent / dir / file
    data = util.load_json_file(placeholder_path)
    ph_data = PlaceHolderData()
    # Build set map
    for s in data.get('sets', []):
        if isinstance(s, dict) and len(s) == 1:
            set_name = list(s.keys())[0]
            values   = s[set_name]
            if not util.isvalid_set(values):
                print(f"Error: Set '{set_name}' is invalid: {values}")
            ph_data.set_map[set_name] = values
    # Build function map
    for f in data.get('functions', []):
        if isinstance(f, dict) and len(f) == 1:
            sig     = list(f.keys())[0]
            mapping = f[sig]
            if not util.isvalid_fun(sig, mapping, ph_data.set_map):
                print(f"Error: Function '{sig}' is invalid: {mapping}")
            ph_data.fun_map[sig] = mapping
    # Build relation map
    for r in data.get('relations', []):
        if isinstance(r, dict) and len(r) == 1:
            sig     = list(r.keys())[0]
            mapping = r[sig]
            if not util.isvalid_rel(sig, mapping, ph_data.set_map):
                print(f"Error: Relation '{sig}' is invalid: {mapping}")
            ph_data.rel_map[sig] = mapping
    # Process auxiliary objects
    ph_data.process_aux_objs()
    # Return placeholder data
    return ph_data
