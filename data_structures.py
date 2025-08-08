#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import regex_constants as rxconst
from re import findall
from re import search
from typing import Callable
from utilities import load_json_file

class BuiltInFunction(dict) :
    def __init__( self, function : Callable[ [str], str]) :
        super().__init__()
        self.function = function
    def __contains__( self, key: object) -> bool :
        return True
    def __getitem__( self, key : str) -> str :
        return self.function(key)
    def __setitem__( self, key : str, value : str) -> None :
        pass

class PlaceHolderDatabase:
    """
    Convenience object for storing all placeholder data
    """
    
    def __init__( self, set_map : dict = {}, fun_map : dict = {}, rel_map : dict = {}) :
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
    
    def add_built_in_functions( self) -> None :
        """
        Add built-in functions like SAME[SET] for every set.
        SAME[SET] is an identity function that returns its argument.
        """
        for set_name in self.set_map.keys():
            same_func_name = f"SAME[{set_name}]"
            self.fun_map[same_func_name] = BuiltInFunction(lambda x: x)
        return
    
    @staticmethod
    def extract_arg_set( set_signature : str) -> str | None :
        """
        Extract the argument set name from a function or relation signature.
        For example, from "ENG[SIDE]" extract "SIDE".
        """
        match = search( rxconst.RX_ARG, set_signature)
        return match.group(1) if match else None
    
    def get_first_placeholder( self, data : str | list[str], ph_type : str) -> str | None :
        """
        Get the first placeholder of a given type in the data
        """
        if isinstance( data, str) :
            placeholders = []
            match ph_type:
                case 'set':
                    placeholders = self.get_placeholder_sets(data)
                case 'fun':
                    placeholders = self.get_placeholder_funs(data)
                case 'rel':
                    placeholders = self.get_placeholder_rels(data)
                case _:
                    raise ValueError(f"Invalid placeholder type: {ph_type}")
            if placeholders:
                return placeholders[0]
        
        elif isinstance( data, list) :
            for item in data:
                first_placeholder = self.get_first_placeholder( item, ph_type)
                if first_placeholder :
                    return first_placeholder
        
        return None
    
    def get_placeholder_sets( self, keyval : str) -> list :
        """
        Get all placeholder sets in keyval
        """
        ph_sets = findall( rxconst.RX_SET_, keyval)
        for ph in ph_sets:
            if ph not in self.set_set:
                print(f"Error: Set '{ph}' not found in signatures")
        return ph_sets
    
    def get_placeholder_funs( self, keyval : str) -> list :
        """
        Get all placeholder functions in keyval
        """
        ph_funs = findall( rxconst.RX_FUN_, keyval)
        ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
        for ph in ph_funs_full:
            if ph not in self.fun_set:
                print(f"Error: Function '{ph}' not found in signatures")
        return ph_funs_full
    
    def get_placeholder_rels( self, keyval : str) -> list :
        """
        Get all placeholder relations in keyval
        """
        ph_rels = findall( rxconst.RX_REL_, keyval)
        ph_rels_full = [f"{rel_name}[{arg_name}]" for rel_name, arg_name in ph_rels]
        for ph in ph_rels_full:
            if ph not in self.rel_set:
                print(f"Error: Relation '{ph}' not found in signatures")
        return ph_rels_full
    
    @staticmethod
    def isvalid_set( set_values : list) -> bool :
        """
        Check placeholder declaration for correctness: sets
        """
        # Check that set_values is not empty
        if not set_values :
            return False
        # Check that all set values are of the same type
        first_type = type(set_values[0])
        if not all( isinstance( val, first_type) for val in set_values ) :
            return False
        # No check failed so set is valid
        return True

    def isvalid_fun( self, fun_signature : str, mapping : dict) -> bool :
        """
        Check placeholder declaration for correctness: functions
        """
        # Check that argument set is in set_map
        match    = search( rxconst.RX_ARG, fun_signature)
        set_name = match.group(1) if match else None
        if not ( set_name and ( set_name in self.set_map ) ) :
            return False
        # Check that mapping has the same number of keys as set_values has elements
        set_values = self.set_map[set_name]
        if len(mapping) != len(set_values) :
            return False
        # Check that every key in mapping is in set_values
        if not all( key in set_values for key in mapping.keys() ) :
            return False
        # No check failed so function is valid
        return True

    def isvalid_rel( self, rel_signature : str, mapping : dict) -> bool :
        """
        Check placeholder declaration for correctness: relations
        """
        # Check the keys as if it were a function
        if not self.isvalid_fun( rel_signature, mapping):
            return False
        # Check that every value in the mapping is a valid set
        for val in mapping.values():
            if not self.isvalid_set(val):
                return False
        return True
    
    @staticmethod
    def replace( argument : str | list[str], 
                 placeholder : str, 
                 placeholder_value : str) -> str | list[str] :
        """
        Replace a set or function placeholder in a string or list of strings
        """
        placeholder_str = f'({placeholder})'
        result = None
        if isinstance( argument, str) :
            result = str(argument).replace( placeholder_str, placeholder_value)
        elif isinstance( argument, list) :
            result = []
            for item in argument :
                new_item = str(item).replace( placeholder_str, placeholder_value)
                result.append(new_item)
        else:
            raise ValueError(f"Invalid argument type: {type(argument)}")
        return result
    
    @staticmethod
    def replace_relation( argument : str | list[str],
                          placeholder : str,
                          placeholder_value : str) -> str | list[str] :
        """
        Replace a relation placeholder in a string or list of strings
        """
        return PlaceHolderDatabase.replace( argument, f'*{placeholder}', placeholder_value)
    
    def update( self) -> None :
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
            self.fun_arg_map[k] = self.extract_arg_set(k)
        for k in self.rel_set:
            self.rel_arg_map[k] = self.extract_arg_set(k)
        # Set of argument sets for functions and relations
        self.fun_arg_set = self.fun_arg_map.values()
        self.rel_arg_set = self.rel_arg_map.values()
        # Return
        return

def load_placeholders( placeholder_path : str) -> PlaceHolderDatabase:
    # Load data
    data = load_json_file(placeholder_path)
    # Initialize placeholder database object
    ph_data = PlaceHolderDatabase()
    
    # Build set map - now directly from the sets dictionary
    sets_data = data.get( 'sets', {})
    for set_name, values in sets_data.items():
        if not ph_data.isvalid_set(values):
            print(f"Error: Set '{set_name}' is invalid: {values}")
        ph_data.set_map[set_name] = values
    
    # Build function map - now directly from the functions dictionary
    functions_data = data.get( 'functions', {})
    for signature, mapping in functions_data.items():
        if not ph_data.isvalid_fun( signature, mapping):
            print(f"Error: Function '{signature}' is invalid: {mapping}")
        ph_data.fun_map[signature] = mapping
    
    # Build relation map - now directly from the relations dictionary
    relations_data = data.get( 'relations', {})
    for signature, mapping in relations_data.items():
        if not ph_data.isvalid_rel( signature, mapping):
            print(f"Error: Relation '{signature}' is invalid: {mapping}")
        ph_data.rel_map[signature] = mapping
    
    # Update auxiliary data structures
    ph_data.update()
    # Return placeholder data
    return ph_data
