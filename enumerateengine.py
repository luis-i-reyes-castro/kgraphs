#!/usr/bin/env python3
"""
New enumeration engine using PlaceHolderDatabase and related data structures.
This is a rewrite of enumerate.py using the new data structures for better
maintainability, type safety, and performance.
"""

import json
import sys
import data_structures as ds
import utilities as util
from pathlib import Path

class EnumerateEngine:
    """
    New enumeration engine using PlaceHolderDatabase for placeholder expansion.
    """
    
    def __init__( self, placeholder_db: ds.PlaceHolderDatabase):
        """
        Initialize the enumeration engine with a placeholder database.
        Args:
            placeholder_db: PlaceHolderDatabase instance containing all placeholder data
        """
        self.ph_db = placeholder_db
    
    def enumerate_json( self, data: dict | list[dict]) -> list[dict]:
        """
        Main entry point for JSON enumeration.
        Args:
            data: JSON data to enumerate (dict or list of dicts)
        Returns:
            List of expanded dictionaries
        """
        if isinstance( data, list):
            # Handle list of dictionaries
            expanded_list = []
            for item in data:
                expanded_items = self.enumerate_dict(item)
                if isinstance(expanded_items, list):
                    expanded_list.extend(expanded_items)
                else:
                    expanded_list.append(expanded_items)
            return expanded_list
        elif isinstance(data, dict):
            # Handle single dictionary
            return self.enumerate_dict(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def enumerate_dict( self, data: dict) -> list[dict]:
        """
        Enumerate a single dictionary.
        Args:
            data: Dictionary to enumerate
        Returns:
            List of expanded dictionaries
        """
        # Get placeholder information for the entire dictionary
        ph_info = self.ph_db.get_placeholders(data)
        
        # Determine expansion strategy based on placeholder locations
        if ph_info.has_phs('keys'):
            # Placeholders in keys - expand keys and create separate objects
            return self._enumerate_with_key_placeholders(data)
        elif ph_info.has_phs( 'values', 'rel'):
            # Relations in values - create multiple objects for each combination
            return self._enumerate_with_relations(data)
        elif ph_info.has_phs( 'values', 'set') or ph_info.has_phs( 'values', 'fun'):
            # Regular placeholders in values - expand based on data type
            return self._enumerate_with_value_placeholders(data)
        else:
            # No placeholders - simple expansion
            return [self._expand_dict_simple(data)]
    
    def _enumerate_with_key_placeholders( self, data: dict) -> list[dict]:
        """
        Handle enumeration when placeholders appear in dictionary keys.
        """
        result = []
        
        # Find all placeholder sets used in keys
        key_placeholder_sets = set()
        for key in data.keys():
            key_phs = self.ph_db.get_placeholder_sets(key)
            key_placeholder_sets.update(key_phs)
        
        # Generate all combinations of key placeholder values
        for set_name in key_placeholder_sets:
            if set_name not in self.ph_db.set_map:
                continue
            
            for set_val in self.ph_db.set_map[set_name]:
                context = {set_name: set_val}
                new_obj = {}
                
                for orig_key, orig_val in data.items():
                    # Expand the key
                    expanded_key = self.ph_db.apply_phs(orig_key, context)
                    if isinstance(expanded_key, list):
                        # Key expansion returned multiple values (shouldn't happen for keys)
                        expanded_key = expanded_key[0] if expanded_key else orig_key
                    
                    # Expand the value
                    expanded_val = self.ph_db.apply_phs(orig_val, context)
                    if isinstance(expanded_val, list):
                        # Value expansion returned multiple values - create separate objects
                        for val in expanded_val:
                            new_obj_copy = new_obj.copy()
                            new_obj_copy[expanded_key] = val
                            result.append(new_obj_copy)
                        break  # Only process this key once since we're creating multiple objects
                    else:
                        new_obj[expanded_key] = expanded_val
                else:
                    # No list returns, add the object
                    result.append(new_obj)
        
        return result if result else [data]
    
    def _enumerate_with_relations( self, data: dict) -> list[dict]:
        """
        Handle enumeration when relations (set-returning functions) appear in values.
        """
        result = []
        
        # Find all placeholder sets that could be used in relations
        all_placeholder_sets = set()
        for key, val in data.items():
            if isinstance(val, str):
                val_rels = self.ph_db.get_placeholder_rels(val)
                for rel_sig in val_rels:
                    arg_set = self.ph_db.rel_arg_map.get(rel_sig)
                    if arg_set:
                        all_placeholder_sets.add(arg_set)
        
        # For each value of each placeholder set, create expansions
        for set_name in all_placeholder_sets:
            for set_val in self.ph_db.set_map[set_name]:
                context = {set_name: set_val}
                new_obj = {}
                
                for orig_key, orig_val in data.items():
                    expanded_val = self.ph_db.apply_phs(orig_val, context)
                    if isinstance(expanded_val, list):
                        # Value expansion returned multiple values - create separate objects
                        for val in expanded_val:
                            new_obj_copy = new_obj.copy()
                            new_obj_copy[orig_key] = val
                            result.append(new_obj_copy)
                        break  # Only process this key once since we're creating multiple objects
                    else:
                        new_obj[orig_key] = expanded_val
                else:
                    # No list returns, add the object
                    result.append(new_obj)
        
        return result if result else [data]
    
    def _enumerate_with_value_placeholders( self, data: dict) -> list[dict]:
        """
        Handle enumeration when regular placeholders appear in values.
        """
        # Find the first placeholder set that appears in values
        first_placeholder_set = None
        for key, val in data.items():
            if isinstance(val, str):
                val_sets = self.ph_db.get_placeholder_sets(val)
                for set_name in val_sets:
                    if set_name in self.ph_db.set_map:
                        first_placeholder_set = set_name
                        break
                if first_placeholder_set:
                    break
        
        if not first_placeholder_set:
            # No valid placeholder sets found
            return [self._expand_dict_simple(data)]
        
        # Check if any value is a list
        has_list_values = any(isinstance(val, list) for val in data.values())
        
        if has_list_values:
            # For lists, expand placeholders within the list elements
            return [self._expand_dict_with_lists(data)]
        else:
            # For simple values, create separate objects for each expansion
            result = []
            for set_val in self.ph_db.set_map[first_placeholder_set]:
                context = {first_placeholder_set: set_val}
                new_obj = {}
                
                for orig_key, orig_val in data.items():
                    expanded_val = self.ph_db.apply_phs(orig_val, context)
                    if isinstance(expanded_val, list):
                        # Value expansion returned multiple values - create separate objects
                        for val in expanded_val:
                            new_obj_copy = new_obj.copy()
                            new_obj_copy[orig_key] = val
                            result.append(new_obj_copy)
                        break  # Only process this key once since we're creating multiple objects
                    else:
                        new_obj[orig_key] = expanded_val
                else:
                    # No list returns, add the object
                    result.append(new_obj)
            
            return result if result else [data]
    
    def _expand_dict_simple( self, data: dict) -> dict:
        """
        Simple expansion of a dictionary with no placeholders.
        """
        result = {}
        for key, val in data.items():
            expanded_val = self.ph_db.apply_phs(val, {})
            if isinstance(expanded_val, list):
                # Take the first value if expansion returns a list
                expanded_val = expanded_val[0] if expanded_val else val
            result[key] = expanded_val
        return result
    
    def _expand_dict_with_lists( self, data: dict) -> dict:
        """
        Expand a dictionary that contains list values.
        """
        result = {}
        for orig_key, orig_val in data.items():
            if isinstance(orig_val, list):
                # Expand placeholders within list elements
                expanded_list = []
                for item in orig_val:
                    if isinstance(item, dict):
                        # Handle dictionary items in lists
                        expanded_item = self._expand_dict_item_in_list(item)
                        if isinstance(expanded_item, list):
                            expanded_list.extend(expanded_item)
                        else:
                            expanded_list.append(expanded_item)
                    else:
                        # Handle simple items in lists
                        expanded_item = self.ph_db.apply_phs(item, {})
                        if isinstance(expanded_item, list):
                            expanded_list.extend(expanded_item)
                        else:
                            expanded_list.append(expanded_item)
                result[orig_key] = expanded_list
            else:
                # Handle non-list values
                expanded_val = self.ph_db.apply_phs(orig_val, {})
                if isinstance(expanded_val, list):
                    expanded_val = expanded_val[0] if expanded_val else orig_val
                result[orig_key] = expanded_val
        return result
    
    def _expand_dict_item_in_list( self, item: dict) -> dict | list[dict]:
        """
        Expand a dictionary item within a list.
        """
        # Check if this dict item has placeholders
        item_ph_info = self.ph_db.get_placeholders(item)
        
        if item_ph_info.has_phs('anywhere', 'set') or item_ph_info.has_phs('anywhere', 'fun') or item_ph_info.has_phs('anywhere', 'rel'):
            # Item has placeholders - find the first placeholder set
            first_placeholder_set = None
            for key, val in item.items():
                if isinstance(val, str):
                    val_sets = self.ph_db.get_placeholder_sets(val)
                    for set_name in val_sets:
                        if set_name in self.ph_db.set_map:
                            first_placeholder_set = set_name
                            break
                    if first_placeholder_set:
                        break
            
            if first_placeholder_set:
                # Create separate items for each placeholder expansion
                result = []
                for set_val in self.ph_db.set_map[first_placeholder_set]:
                    context = {first_placeholder_set: set_val}
                    expanded_item = {}
                    
                    for item_key, item_val in item.items():
                        expanded_item_val = self.ph_db.apply_phs(item_val, context)
                        if isinstance(expanded_item_val, list):
                            # Create separate items for each value
                            for val in expanded_item_val:
                                expanded_item_copy = expanded_item.copy()
                                expanded_item_copy[item_key] = val
                                result.append(expanded_item_copy)
                            break  # Only process this key once since we're creating multiple items
                        else:
                            expanded_item[item_key] = expanded_item_val
                    else:
                        # No list returns, add the item
                        result.append(expanded_item)
                
                return result if result else [item]
            else:
                # No valid placeholder sets, expand normally
                return self._expand_dict_simple(item)
        else:
            # No placeholders, expand normally
            return self._expand_dict_simple(item)

def load_placeholders_newlang() -> ds.PlaceHolderDatabase:
    """
    Load placeholders from the newlang directory using the new format.
    """
    return ds.load_placeholders( 'newlang', 'placeholders.json')

def main():
    """
    Main function for command-line usage.
    """
    if len(sys.argv) != 2:
        print("Usage: python enumerate_new.py <input_json_file>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ Input file {input_path} does not exist.")
        sys.exit(1)
    
    # Try to load placeholders from newlang first, fall back to json
    try:
        placeholder_db = load_placeholders_newlang()
        print("✅ Loaded placeholders from newlang/placeholders.json")
    except FileNotFoundError:
        print("❌ Could not find placeholders.json in either newlang/ or json/ directories")
        sys.exit(1)
    
    # Load and enumerate the JSON data
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    engine = EnumerateEngine(placeholder_db)
    expanded = engine.enumerate_json(data)
    
    # Write the result
    out_dir = Path(__file__).parent / 'enum'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / input_path.name
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(expanded, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"✅ Wrote enumerated cases to {out_path}")


if __name__ == "__main__":
    main()
