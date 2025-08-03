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
        self.sets = set()
        self.funs = set()
        self.rels = set()
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
    def print( self, name = 'String') -> None:
        print(f"{name} Placeholders:")
        print(f"  Data: {self.data}")
        print(f"  Sets: {self.sets}")
        print(f"  Functions: {self.funs}")
        print(f"  Relations: {self.rels}")
        return

class PlaceHoldersInDict:
    
    def __init__( self, data : dict):
        self.data = data
        self.leads_to_str = { key : isinstance( val, str) for key, val in self.data.items() }
        self.key_phs          = { key : PlaceHoldersInStr() for key in data.keys() }
        self.val_phs          = { key : PlaceHoldersInStr() for key in data.keys() }
        self.combined_key_phs = PlaceHoldersInStr()
        self.combined_val_phs = PlaceHoldersInStr()
        self.combined_phs     = PlaceHoldersInStr()
        return
    
    def update( self) -> None:
        for key in self.data.keys():
            # Keys are always strings
            self.combined_key_phs.sets.update(self.key_phs[key].sets)
            self.combined_key_phs.funs.update(self.key_phs[key].funs)
            self.combined_key_phs.rels.update(self.key_phs[key].rels)
            self.combined_phs.sets.update(self.key_phs[key].sets)
            self.combined_phs.funs.update(self.key_phs[key].funs)
            self.combined_phs.rels.update(self.key_phs[key].rels)
            # Values may be strings or data structures
            if self.leads_to_str[key]:
                self.combined_val_phs.sets.update(self.val_phs[key].sets)
                self.combined_val_phs.funs.update(self.val_phs[key].funs)
                self.combined_val_phs.rels.update(self.val_phs[key].rels)
                self.combined_phs.sets.update(self.val_phs[key].sets)
                self.combined_phs.funs.update(self.val_phs[key].funs)
                self.combined_phs.rels.update(self.val_phs[key].rels)
        return
    
    def contains( self, location : str, placeholder_type : str) -> bool:
        data_struct = None
        match location:
            case 'keys':
                data_struct = self.combined_key_phs
            case 'vals':
                data_struct = self.combined_val_phs
            case 'anywhere':
                data_struct = self.combined_phs
            case _:
                raise ValueError(f"Invalid location: {location}")
        match placeholder_type:
            case 'set':
                return len(data_struct.sets) > 0
            case 'fun':
                return len(data_struct.funs) > 0
            case 'rel':
                return len(data_struct.rels) > 0
            case 'any':
                return len(data_struct.sets) > 0 or \
                       len(data_struct.funs) > 0 or \
                       len(data_struct.rels) > 0
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return False
    
    def contains_only_strings( self) -> bool:
        return all(self.leads_to_str.values())
    
    def contains_data_structures( self) -> bool:
        return not self.contains_only_strings()
    
    def print( self) -> None:
        print('PLACEHOLDERS IN DICT:')
        self.combined_phs.print('Combined Key and Val')
        self.combined_key_phs.print('Combined Key')
        self.combined_val_phs.print('Combined Val')
        for key in self.data.keys():
            self.key_phs[key].print('Key')
            if self.leads_to_str[key]:
                self.val_phs[key].print('Value')
        return

class PlaceHoldersInList:
    
    def __init__( self, data : list):
        self.data = data
        self.leads_to_str = [ isinstance( item, str) for item in self.data ]
        self.item_phs     = [ PlaceHoldersInStr() for _ in self.data ]
        self.combined_phs = PlaceHoldersInStr()
        return
    
    def update( self) -> None:
        for i, _ in enumerate(self.data):
            if self.leads_to_str[i]:
                self.combined_phs.sets.update(self.item_phs[i].sets)
                self.combined_phs.funs.update(self.item_phs[i].funs)
                self.combined_phs.rels.update(self.item_phs[i].rels)
        return
    
    def contains( self, placeholder_type : str) -> bool:
        match placeholder_type:
            case 'set':
                return len(self.combined_phs.sets) > 0
            case 'fun':
                return len(self.combined_phs.funs) > 0
            case 'rel':
                return len(self.combined_phs.rels) > 0
            case 'any':
                return len(self.combined_phs.sets) > 0 or \
                       len(self.combined_phs.funs) > 0 or \
                       len(self.combined_phs.rels) > 0
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return False
    
    def contains_only_strings( self) -> bool:
        return all(self.leads_to_str)
    
    def contains_data_structures( self) -> bool:
        return not self.contains_only_strings()
    
    def print( self) -> None:
        print('PLACEHOLDERS IN LIST:')
        self.combined_phs.print('Combined Items')
        for i, item in enumerate(self.data):
            if self.leads_to_str[i]:
                self.item_phs[i].print('Item')
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
        self.set_set = set()
        self.fun_set = set()
        self.rel_set = set()
        self.fun_arg_map = {}
        self.rel_arg_map = {}
        self.fun_arg_set = set()
        self.rel_arg_set = set()
        return
    
    def update(self) -> None:
        """
        Update auxiliary data structures
        """
        # Add built-in functions first
        self.add_built_in_functions()
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
    
    def add_built_in_functions(self) -> None:
        """
        Add built-in functions like SAME[SET] for every set.
        SAME[SET] is an identity function that returns its argument.
        """
        for set_name in self.set_map.keys():
            same_func_name = f"SAME[{set_name}]"
            self.fun_map[same_func_name] = BuiltInFunction(lambda x: x)
        return
    
    def get_placeholder_sets( self, keyval : str) -> set:
        """
        Get all placeholder sets in keyval
        """
        ph_sets = findall( rxconst.RX_SET_, keyval)
        for ph in ph_sets:
            if ph not in self.set_set:
                print(f"Error: Set '{ph}' not found in signatures")
        return set(ph_sets)
    
    def get_placeholder_funs( self, keyval : str) -> set:
        """
        Get all placeholder functions in keyval
        """
        ph_funs = findall( rxconst.RX_FUN_, keyval)
        ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
        for ph in ph_funs_full:
            if ph not in self.fun_set:
                print(f"Error: Function '{ph}' not found in signatures")
        return set(ph_funs_full)
    
    def get_placeholder_rels( self, keyval : str) -> set:
        """
        Get all placeholder relations in keyval
        """
        ph_rels = findall( rxconst.RX_REL_, keyval)
        ph_rels_full = [f"{rel_name}[{arg_name}]" for rel_name, arg_name in ph_rels]
        for ph in ph_rels_full:
            if ph not in self.rel_set:
                print(f"Error: Relation '{ph}' not found in signatures")
        return set(ph_rels_full)

    def get_placeholders( self, data : str | dict | list
                        ) -> PlaceHoldersInStr | PlaceHoldersInDict | PlaceHoldersInList:
        """
        Get all placeholders in keyval
        """
        result = None

        if isinstance( data, str):
            result = PlaceHoldersInStr(data)
            result.sets = self.get_placeholder_sets(data)
            result.funs = self.get_placeholder_funs(data)
            result.rels = self.get_placeholder_rels(data)

        elif isinstance( data, dict):
            result = PlaceHoldersInDict(data)
            for k, v in data.items():
                result.key_phs[k].data = k
                result.key_phs[k].sets = self.get_placeholder_sets(k)
                result.key_phs[k].funs = self.get_placeholder_funs(k)
                result.key_phs[k].rels = self.get_placeholder_rels(k)
                if result.leads_to_str[k]:
                    result.val_phs[k].data = v
                    result.val_phs[k].sets = self.get_placeholder_sets(v)
                    result.val_phs[k].funs = self.get_placeholder_funs(v)
                    result.val_phs[k].rels = self.get_placeholder_rels(v)
            result.update()
        
        elif isinstance( data, list):
            result = PlaceHoldersInList(data)
            for i, item in enumerate(data):
                if result.leads_to_str[i]:
                    result.item_phs[i].data = item
                    result.item_phs[i].sets = self.get_placeholder_sets(item)
                    result.item_phs[i].funs = self.get_placeholder_funs(item)
                    result.item_phs[i].rels = self.get_placeholder_rels(item)
            result.update()
        
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
