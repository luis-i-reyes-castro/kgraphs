#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import dka_regex as phrx
from re import findall
from re import search
from typing import Callable
from utilities_io import load_json_file

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
    
    def __init__(self) -> None :
        """
        Initialize placeholder data
        """
        self.set_map = {} # str_set_name : list_elements
        self.sub_map = {} # str_set_name : list_subsets
        self.fun_map = {} # str_fun_name : dict_function_implementation
        return
    
    def add_built_in_functions( self) -> None :
        """
        Add built-in functions like SAME[SET] for every set.
        SAME[SET] is an identity function that returns its argument.
        """
        for set_name in self.set_map :
            same_func_name = f"SAME[{set_name}]"
            self.fun_map[same_func_name] = BuiltInFunction(lambda x: x)
        return
    
    def extract_arg_set( self, fun_call : str) -> str | None :
        """
        Extract the argument set name from a function call.
        For example, from "ENG[SIDE]" extract "SIDE".
        """
        match = search( phrx.RX_ARG, fun_call)
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
        ph_sets = findall( phrx.RX_SET_, keyval)
        for ph in ph_sets :
            if ph not in self.set_map :
                print(f"Error: Set '{ph}' not found in signatures")
        return ph_sets
    
    def get_placeholder_funs( self, keyval : str) -> list :
        """
        Get all placeholder functions in keyval
        """
        ph_funs = findall( phrx.RX_FUN_, keyval)
        ph_funs_full = [f"{func_name}[{arg_name}]" for func_name, arg_name in ph_funs]
        for ph in ph_funs_full :
            if ph not in self.fun_map :
                print(f"Error: Function '{ph}' not found in signatures")
        return ph_funs_full
    
    def is_valid_set( self, set_elements : list) -> bool :
        """
        Check placeholder declaration for correctness: sets
        """
        # Check that set has at least two elements
        if not len(set_elements) >= 2 :
            return False
        # Check that set elements are of the same type
        first_type = type(set_elements[0])
        if not all( isinstance( val, first_type) for val in set_elements ) :
            return False
        # Check that set elements are unique
        if not len(set_elements) == len(set(set_elements)) :
            return False
        # No check failed so set is valid
        return True
    
    def is_valid_sub( self, superset : str, sub_elements : list) -> bool :
        # Check that superset exists
        if not superset in self.set_map :
            return False
        # Check that subset is a valid set
        if not self.is_valid_set(sub_elements) :
            return False
        # Check that subset elements are in superset
        for element in sub_elements :
            if not element in self.set_map[superset] :
                return False
        # No check failed so subset is valid
        return True

    def is_valid_fun( self, fun_name : str, fun_dict : dict) -> bool :
        """
        Check placeholder declaration for correctness: functions
        """
        # Check that function argument is in set_map
        set_name = self.extract_arg_set(fun_name)
        if not ( set_name and ( set_name in self.set_map ) ) :
            return False
        # Check that function domain matches argument
        set_elements = self.set_map[set_name]
        if not all( ( element in fun_dict ) for element in set_elements ) :
            return False
        if not all( ( element in set_elements ) for element in fun_dict ) :
            return False
        # No check failed so function is valid
        return True
    
    def replace( self,
                 argument : str,
                 placeholder : str,
                 placeholder_value : str) -> str :
        """
        Replace a set or function placeholder in a string or list of strings
        """
        result = None
        if isinstance( argument, str) :
            result = str(argument).replace( f'({placeholder})', placeholder_value)
        else:
            raise ValueError(f"Invalid argument type: {type(argument)}")
        return result

def load_placeholders( placeholder_path : str) -> PlaceHolderDatabase:
    # Load data
    data = load_json_file(placeholder_path)
    # Initialize placeholder database object
    phDB = PlaceHolderDatabase()
    
    # Build set map
    sets_data = data.get( 'sets', {})
    for set_name, set_elements in sets_data.items() :
        if not phDB.is_valid_set(set_elements) :
            print(f"Error: Set '{set_name}' is invalid: {set_elements}")
        phDB.set_map[set_name] = set_elements
        phDB.sub_map[set_name] = []
    
    # Process subsets
    subs_data = data.get( 'subsets', {})
    for sub_name, sub_dict in subs_data.items() :
        # Get superset and elements
        superset     = sub_dict.get( 'set', '')
        sub_elements = sub_dict.get( 'elements', [])
        # Check that subset is valid
        if not phDB.is_valid_sub( superset, sub_elements) :
            print(f"Error: Subset '{sub_name}' is invalid: {sub_elements}")
        # Add to set and subset maps
        phDB.set_map[sub_name] = sub_elements
        phDB.sub_map[superset].append(sub_name)
    
    # Build function map
    data = data.get( 'functions', {})
    for fun_name, fun_dict in data.items() :
        if not phDB.is_valid_fun( fun_name, fun_dict) :
            print(f"Error: Function '{fun_name}' is invalid: {fun_dict}")
        phDB.fun_map[fun_name] = fun_dict
    
    # Process functions of subsets
    funs_of_subsets = {}
    for fun_name, fun_dict in phDB.fun_map.items() :
        fun_arg = phDB.extract_arg_set(fun_name)
        if fun_arg in phDB.sub_map :
            for subset in phDB.sub_map[fun_arg] :
                new_fun_name = fun_name.replace( fun_arg, subset)
                if not new_fun_name in phDB.fun_map :
                    funs_of_subsets[new_fun_name] = {}
                    for element in phDB.set_map[subset] :
                        funs_of_subsets[new_fun_name][element]= fun_dict[element]
    if funs_of_subsets :
        phDB.fun_map.update(funs_of_subsets)
    
    # Add built-in functions
    phDB.add_built_in_functions()

    # Return placeholder data
    return phDB
