#!/usr/bin/env python3
"""
Data structures for placeholder substitution
"""

import regex_constants as rxconst
import utilities as util
from pathlib import Path
from re import findall

class PlaceHoldersInStr:
    def __init__( self, data : str | None = None):
        self.data = data
        self.sets = set()
        self.funs = set()
        self.rels = set()
        return

class PlaceHoldersInDict:
    
    def __init__( self, data : dict):
        self.data = data
        self.key_phs = { key : PlaceHoldersInStr() for key in data.keys()   }
        self.val_phs = { key : PlaceHoldersInStr() for key in data.values() }
        self.combined_key_phs = PlaceHoldersInStr()
        self.combined_val_phs = PlaceHoldersInStr()
        self.combined_phs     = PlaceHoldersInStr()
        self.leads_to_dict = { key : False for key in self.data.keys() }
        self.leads_to_list = { key : False for key in self.data.keys() }
        return
    
    def update( self):
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

class PlaceHoldersInList:
    def __init__( self, data : list):
        self.data = data
        self.item_phs = [ PlaceHoldersInStr() for _ in self.data ]
        self.combined_phs = PlaceHoldersInStr()
        self.leads_to_dict = [ False for _ in self.data ]
        self.leads_to_list = [ False for _ in self.data ]
        return
    def update( self):
        for i, _ in enumerate(self.data):
            # Skip if item leads to dict or list
            if self.leads_to_dict[i] or self.leads_to_list[i]:
                continue
            # Update item placeholder data
            self.combined_phs.sets.update(self.item_phs[i].sets)
            self.combined_phs.funs.update(self.item_phs[i].funs)
            self.combined_phs.rels.update(self.item_phs[i].rels)
        return

class PlaceHolderData:
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
