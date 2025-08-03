#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import regex_constants as rxconst
import utilities as util
from pathlib import Path
from re import findall
from typing import Callable

class PlaceHoldersInStr:
    def __init__( self, data : str | None = None):
        self.data = data
        self.sets = []
        self.funs = []
        self.rels = []
        return
    def contains( self, placeholder_type : str) -> bool:
        match placeholder_type:
            case 'set':
                return len(self.sets) > 0
            case 'fun':
                return len(self.funs) > 0
            case 'rel':
                return len(self.rels) > 0
            case 'any':
                return len(self.sets) > 0 or \
                       len(self.funs) > 0 or \
                       len(self.rels) > 0
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return False
    def print( self, indent = 1) -> None:
        spaces = '  ' * indent
        print(f"{spaces}Sets: {self.sets}")
        print(f"{spaces}Functions: {self.funs}")
        print(f"{spaces}Relations: {self.rels}")
        return

class BuiltInFunction(dict):
    def __init__( self, function : Callable[ [str], str]):
        super().__init__()
        self.function = function
    def __contains__( self, key: object) -> bool:
        return True
    def __getitem__( self, key : str) -> str:
        return self.function(key)
    def __setitem__( self, key : str, value : str) -> None:
        pass

class PlaceHolderDatabase:
    """
    Convenience object for storing all placeholder data
    """
    
    def __init__(self, set_map : dict = {}, fun_map : dict = {}, rel_map : dict = {}):
        """
        Initialize placeholder data
        """
        self.set_map = set_map
        self.fun_map = fun_map
        self.rel_map = rel_map
        self.set_set = []
        self.fun_set = []
        self.rel_set = []
        self.fun_arg_map = {}
        self.rel_arg_map = {}
        self.fun_arg_set = []
        self.rel_arg_set = []
        return
    
    def update(self) -> None:
        """
        Update auxiliary data structures
        """
        # Add built-in functions first
        self.add_built_in_functions()
        # Set of sets, functions and relations
        self.set_set = self.set_map.keys()
        self.fun_set = self.fun_map.keys()
        self.rel_set = self.rel_map.keys()
        # Map of functions and relations to their argument sets
        for k in self.fun_set:
            self.fun_arg_map[k] = util.extract_arg_set(k)
        for k in self.rel_set:
            self.rel_arg_map[k] = util.extract_arg_set(k)
        # Set of argument sets for functions and relations
        self.fun_arg_set = self.fun_arg_map.values()
        self.rel_arg_set = self.rel_arg_map.values()
        # Return
        return
    
    def add_built_in_functions(self) -> None:
        """
        Add built-in functions like SAME[SET] for every set.
        SAME[SET] is an identity function that returns its argument.
        """
        for set_name in self.set_map.keys():
            same_func_name = f"SAME[{set_name}]"
            self.fun_map[same_func_name] = BuiltInFunction(lambda x: x)
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

    def get_placeholders( self, data : str) -> PlaceHoldersInStr :
        """
        Get all placeholders in keyval
        """
        result = None

        if isinstance( data, str):
            result = PlaceHoldersInStr(data)
            result.sets = self.get_placeholder_sets(data)
            result.funs = self.get_placeholder_funs(data)
            result.rels = self.get_placeholder_rels(data)
        else:
            raise ValueError(f"Invalid data type: {type(data)}")
        
        return result

def load_placeholders( dir: str = 'newlang',
                       file: str = 'placeholders.json') -> PlaceHolderDatabase:
    # Load data
    placeholder_path = Path(__file__).parent / dir / file
    data = util.load_json_file(placeholder_path)
    ph_data = PlaceHolderDatabase()
    
    # Build set map - now directly from the sets dictionary
    sets_data = data.get('sets', {})
    for set_name, values in sets_data.items():
        if not util.isvalid_set(values):
            print(f"Error: Set '{set_name}' is invalid: {values}")
        ph_data.set_map[set_name] = values
    
    # Build function map - now directly from the functions dictionary
    functions_data = data.get('functions', {})
    for sig, mapping in functions_data.items():
        if not util.isvalid_fun(sig, mapping, ph_data.set_map):
            print(f"Error: Function '{sig}' is invalid: {mapping}")
        ph_data.fun_map[sig] = mapping
    
    # Build relation map - now directly from the relations dictionary
    relations_data = data.get('relations', {})
    for sig, mapping in relations_data.items():
        if not util.isvalid_rel(sig, mapping, ph_data.set_map):
            print(f"Error: Relation '{sig}' is invalid: {mapping}")
        ph_data.rel_map[sig] = mapping
    
    # Update auxiliary data structures
    ph_data.update()
    # Return placeholder data
    return ph_data
