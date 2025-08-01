#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import itertools
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
    def has_phs( self, placeholder_type : str) -> bool:
        data_struct_phs = None
        match placeholder_type:
            case 'set':
                data_struct_phs = self.sets
            case 'fun':
                data_struct_phs = self.funs
            case 'rel':
                data_struct_phs = self.rels
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return len(data_struct_phs) > 0

class PlaceHoldersInDict:
    
    def __init__( self, data : dict):
        self.data = data
        self.key_phs = { key : PlaceHoldersInStr() for key in data.keys() }
        self.val_phs = { key : PlaceHoldersInStr() for key in data.keys() }
        self.combined_key_phs = PlaceHoldersInStr()
        self.combined_val_phs = PlaceHoldersInStr()
        self.combined_phs     = PlaceHoldersInStr()
        self.leads_to_dict = { key : False for key in self.data.keys() }
        self.leads_to_list = { key : False for key in self.data.keys() }
        return
    
    def update( self) -> None:
        for key in self.data.keys():
            # Skip if key leads to dict or list
            if self.leads_to_dict[key] or self.leads_to_list[key]:
                continue
            # Update combined key and value placeholder data
            self.combined_key_phs.sets.update(self.key_phs[key].sets)
            self.combined_key_phs.funs.update(self.key_phs[key].funs)
            self.combined_key_phs.rels.update(self.key_phs[key].rels)
            self.combined_val_phs.sets.update(self.val_phs[key].sets)
            self.combined_val_phs.funs.update(self.val_phs[key].funs)
            self.combined_val_phs.rels.update(self.val_phs[key].rels)
            # Update combined placeholder data
            self.combined_phs.sets.update(self.key_phs[key].sets)
            self.combined_phs.funs.update(self.key_phs[key].funs)
            self.combined_phs.rels.update(self.key_phs[key].rels)
            self.combined_phs.sets.update(self.val_phs[key].sets)
            self.combined_phs.funs.update(self.val_phs[key].funs)
            self.combined_phs.rels.update(self.val_phs[key].rels)
        return
    
    def has_phs( self, location : str, placeholder_type : str) -> bool:
        data_struct = None
        match location:
            case 'anywhere':
                data_struct = self.combined_phs
            case 'keys':
                data_struct = self.combined_key_phs
            case 'values':
                data_struct = self.combined_val_phs
            case _:
                raise ValueError(f"Invalid location: {location}")
        data_struct_phs = None
        match placeholder_type:
            case 'set':
                data_struct_phs = data_struct.sets
            case 'fun':
                data_struct_phs = data_struct.funs
            case 'rel':
                data_struct_phs = data_struct.rels
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return len(data_struct_phs) > 0
    
    def lead_to_dict( self) -> bool:
        return any(self.leads_to_dict.values())
    
    def lead_to_list( self) -> bool:
        return any(self.leads_to_list.values())

class PlaceHoldersInList:
    def __init__( self, data : list):
        self.data = data
        self.item_phs = [ PlaceHoldersInStr() for _ in self.data ]
        self.combined_phs = PlaceHoldersInStr()
        self.leads_to_dict = [ False for _ in self.data ]
        self.leads_to_list = [ False for _ in self.data ]
        return
    def update( self) -> None:
        for i, _ in enumerate(self.data):
            # Skip if item leads to dict or list
            if self.leads_to_dict[i] or self.leads_to_list[i]:
                continue
            # Update item placeholder data
            self.combined_phs.sets.update(self.item_phs[i].sets)
            self.combined_phs.funs.update(self.item_phs[i].funs)
            self.combined_phs.rels.update(self.item_phs[i].rels)
        return
    def has_phs( self, placeholder_type : str) -> bool:
        data_struct_phs = None
        match placeholder_type:
            case 'set':
                data_struct_phs = self.combined_phs.sets
            case 'fun':
                data_struct_phs = self.combined_phs.funs
            case 'rel':
                data_struct_phs = self.combined_phs.rels
            case _:
                raise ValueError(f"Invalid placeholder type: {placeholder_type}")
        return len(data_struct_phs) > 0
    def lead_to_dict( self) -> bool:
        return any(self.leads_to_dict)
    def lead_to_list( self) -> bool:
        return any(self.leads_to_list)

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
                if isinstance( v, dict):
                    result.leads_to_dict[k] = True
                    continue
                elif isinstance( v, list):
                    result.leads_to_list[k] = True
                    continue
                else:
                    result.val_phs[k].data = v
                    result.val_phs[k].sets = self.get_placeholder_sets(v)
                    result.val_phs[k].funs = self.get_placeholder_funs(v)
                    result.val_phs[k].rels = self.get_placeholder_rels(v)
            result.update()
        
        elif isinstance( data, list):
            result = PlaceHoldersInList(data)
            for i, item in enumerate(data):
                if isinstance( item, dict):
                    result.leads_to_dict[i] = True
                    continue
                elif isinstance( item, list):
                    result.leads_to_list[i] = True
                    continue
                else:
                    result.item_phs[i].data = item
                    result.item_phs[i].sets = self.get_placeholder_sets(item)
                    result.item_phs[i].funs = self.get_placeholder_funs(item)
                    result.item_phs[i].rels = self.get_placeholder_rels(item)
            result.update()
        
        return result
    
    def apply_phs( self, val : str | dict | list, set_context : dict) -> str | list:
        """
        Expand placeholders and function calls within a single value.
        
        Args:
            val: The value to expand (can be string, dict, list, or other types)
            set_context: Dictionary containing set context for placeholder substitution
        
        Returns:
            Either a single expanded value or a list of expanded values (for relations)
        """
        if isinstance( val, str):
            # Check if any relations are present
            ph_rels = self.get_placeholder_rels(val)
            if not ph_rels:
                # Handle regular functions and set placeholders
                return self.apply_phs_regular(val, set_context)
            else:
                # Handle relations (set-returning functions) by creating multiple expansions
                return self.apply_phs_with_relations(val, set_context)
        elif isinstance( val, dict):
            # Recursively expand dictionary values
            result = {}
            for k, v in val.items():
                result[k] = self.apply_phs(v, set_context)
            return result
        elif isinstance( val, list):
            # Recursively expand list elements
            result = []
            for v in val:
                result.append(self.apply_phs(v, set_context))
            return result
        # Return unchanged for other types
        return val
    
    def apply_phs_regular( self, val : str, set_context : dict) -> str:
        """
        Expand regular functions and set placeholders (no relations).
        Returns a single expanded string.
        """
        result = val

        # Replace set calls
        for set_name, set_val in set_context.items():
            result = util.replace_placeholder(result, set_val, set_name)
        
        # Replace function calls
        for func_sig, mapping in self.fun_map.items():
            # Get the argument set name from the pre-computed map
            arg_set = self.fun_arg_map[func_sig]
            if arg_set and arg_set in set_context:
                arg_val = set_context[arg_set]
                if arg_val in mapping:
                    replacement = mapping[arg_val]
                    result = util.replace_placeholder(result, replacement, func_sig)
        
        return result
    
    def apply_phs_with_relations( self, val : str, set_context : dict) -> list:
        """
        Expand values that contain relations (set-returning functions).
        Returns a list of expanded strings.
        """
        # Collect all possible expansions for each relation
        relation_expansions = []
        
        for rel_sig, mapping in self.rel_map.items():
            # Get the argument set name from the pre-computed map
            arg_set = self.rel_arg_map[rel_sig]
            if arg_set and arg_set in set_context:
                arg_val = set_context[arg_set]
                if arg_val in mapping:
                    # Get the list of values returned by this relation
                    relation_values = mapping[arg_val]
                    relation_expansions.append((rel_sig, relation_values))
        
        if not relation_expansions:
            # No valid relations found, fall back to regular expansion
            return self.apply_phs_regular(val, set_context)
        
        # Generate all combinations of relation expansions
        results = []
        rel_sigs = [exp[0] for exp in relation_expansions]
        rel_value_lists = [exp[1] for exp in relation_expansions]
        
        for combination in itertools.product(*rel_value_lists):
            expanded_val = val
            
            # Replace each relation with its value from the combination
            for rel_sig, replacement in zip(rel_sigs, combination):
                # For relations, we need to include the * prefix in the placeholder
                full_placeholder = f"*{rel_sig}"
                expanded_val = util.replace_placeholder(expanded_val, replacement, full_placeholder)
            
            # Also replace any remaining regular functions and set placeholders
            expanded_val = self.apply_phs_regular(expanded_val, set_context)
            
            results.append(expanded_val)
        
        return results

def load_placeholders( dir: str = 'newlang',
                       file: str = 'placeholders.json') -> PlaceHolderDatabase:
    # Load data
    placeholder_path = Path(__file__).parent / dir / file
    data = util.load_json_file(placeholder_path)
    ph_data = PlaceHolderDatabase()
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
    # Update auxiliary data structures
    ph_data.update()
    # Return placeholder data
    return ph_data
