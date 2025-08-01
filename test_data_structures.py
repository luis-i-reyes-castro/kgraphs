#!/usr/bin/env python3
"""
Test script for data_structures.py using test JSON files in newlang/
"""

import json
import sys
from pathlib import Path
from data_structures import PlaceHolderDatabase, load_placeholders, PlaceHoldersInStr, PlaceHoldersInDict, PlaceHoldersInList
from utilities import load_json_file
import regex_constants as rxconst

def test_load_placeholders():
    """Test load_placeholders function"""
    print("Testing load_placeholders...")
    
    try:
        ph_data = load_placeholders()
        
        print(f"  ✓ Successfully loaded placeholders")
        print(f"    Sets: {list(ph_data.set_map.keys())}")
        print(f"    Functions: {list(ph_data.fun_map.keys())}")
        print(f"    Relations: {list(ph_data.rel_map.keys())}")
        
        # Test some specific values
        print(f"    SIDE set: {ph_data.set_map.get('SIDE', 'Not found')}")
        print(f"    ENG[SIDE] function: {ph_data.fun_map.get('ENG[SIDE]', 'Not found')}")
        print(f"    MOTOR[ARM] relation: {ph_data.rel_map.get('MOTOR[ARM]', 'Not found')}")
        
        # Test auxiliary objects
        print(f"    Set set: {ph_data.set_set}")
        print(f"    Function set: {ph_data.fun_set}")
        print(f"    Relation set: {ph_data.rel_set}")
        print(f"    Function arg map: {ph_data.fun_arg_map}")
        print(f"    Relation arg map: {ph_data.rel_arg_map}")
        
    except Exception as e:
        print(f"  ✗ Error loading placeholders: {e}")

def test_PlaceHolderDatabase_class():
    """Test PlaceHolderDatabase class"""
    print("\nTesting PlaceHolderDatabase class...")
    
    # Create test data
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    
    # Create PlaceHolderDatabase object
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    print(f"  Set set: {ph_data.set_set}")
    print(f"  Function set: {ph_data.fun_set}")
    print(f"  Relation set: {ph_data.rel_set}")
    print(f"  Function arg map: {ph_data.fun_arg_map}")
    print(f"  Relation arg map: {ph_data.rel_arg_map}")
    
    assert "SIDE" in ph_data.set_set
    assert "ENG[SIDE]" in ph_data.fun_set
    assert "MOTOR[ARM]" in ph_data.rel_set
    assert ph_data.fun_arg_map["ENG[SIDE]"] == "SIDE"
    assert ph_data.rel_arg_map["MOTOR[ARM]"] == "ARM"

def test_get_placeholder_sets():
    """Test get_placeholder_sets method"""
    print("\nTesting get_placeholder_sets method...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test strings with set placeholders
    test_strings = [
        "aux_light_(SIDE)",
        "rtk_cable_(SIDE)",
        "m(ARM)_esc_cable",
        "no_placeholder",
        "multiple_(SIDE)_(ARM)"
    ]
    
    for test_str in test_strings:
        ph_sets = ph_data.get_placeholder_sets(test_str)
        print(f"  '{test_str}': {ph_sets}")

def test_get_placeholder_funs():
    """Test get_placeholder_funs method"""
    print("\nTesting get_placeholder_funs method...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test strings with function placeholders
    test_strings = [
        "ENG[SIDE]",
        "SPA[SIDE]",
        "ESC[MOTOR]",
        "no_function",
        "multiple_ENG[SIDE]_SPA[SIDE]"
    ]
    
    for test_str in test_strings:
        ph_funs = ph_data.get_placeholder_funs(test_str)
        print(f"  '{test_str}': {ph_funs}")

def test_get_placeholder_rels():
    """Test get_placeholder_rels method"""
    print("\nTesting get_placeholder_rels method...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test strings with relation placeholders
    test_strings = [
        "MOTOR[ARM]",
        "ESC[MOTOR]",
        "no_relation",
        "multiple_MOTOR[ARM]_ESC[MOTOR]"
    ]
    
    for test_str in test_strings:
        ph_rels = ph_data.get_placeholder_rels(test_str)
        print(f"  '{test_str}': {ph_rels}")

def test_get_placeholders_string():
    """Test get_placeholders method with string input"""
    print("\nTesting get_placeholders method with string input...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test strings with various placeholders
    test_strings = [
        "aux_light_(SIDE)",
        "ENG[SIDE]",
        "MOTOR[ARM]",
        "rtk_cable_(SIDE)",
        "m(ARM)_esc_cable",
        "esc_(*MOTOR[ARM])"
    ]
    
    for test_str in test_strings:
        result = ph_data.get_placeholders(test_str)
        print(f"  '{test_str}':")
        print(f"    Sets: {result.sets}")
        print(f"    Functions: {result.funs}")
        print(f"    Relations: {result.rels}")

def test_get_placeholders_dict():
    """Test get_placeholders method with dictionary input"""
    print("\nTesting get_placeholders method with dictionary input...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test simple dictionary first
    simple_dict = {
        "key1": "value1",
        "key2": "value2"
    }
    
    print(f"  Simple dictionary test:")
    result = ph_data.get_placeholders(simple_dict)
    print(f"    Combined sets: {result.combined_phs.sets}")
    print(f"    Key placeholders:")
    for key in simple_dict.keys():
        print(f"      '{key}': {result.key_phs[key].sets}")
    
    # Test dictionary with placeholders
    test_dict = {
        "aux_light_(SIDE)": "ENG[SIDE]",
        "rtk_cable_(SIDE)": "SPA[SIDE]",
        "m(ARM)_esc_cable": "MOTOR[ARM]",
        "no_placeholder": "no_value"
    }
    
    print(f"  Placeholder dictionary test:")
    result = ph_data.get_placeholders(test_dict)
    print(f"    Combined sets: {result.combined_phs.sets}")
    print(f"    Combined functions: {result.combined_phs.funs}")
    print(f"    Combined relations: {result.combined_phs.rels}")
    
    # Test individual key placeholders
    print(f"    Key placeholders:")
    for key in test_dict.keys():
        print(f"      '{key}': {result.key_phs[key].sets}")
    
    # Test individual value placeholders
    print(f"    Value placeholders:")
    print(f"      val_phs keys: {list(result.val_phs.keys())}")
    for value in test_dict.values():
        if value in result.val_phs:
            print(f"      '{value}': {result.val_phs[value].sets}")
        else:
            print(f"      '{value}': Not found in val_phs")

def test_get_placeholders_list():
    """Test get_placeholders method with list input"""
    print("\nTesting get_placeholders method with list input...")
    
    # Create PlaceHolderDatabase object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderDatabase(set_map, func_map, rel_map)
    ph_data.update()
    
    # Test list with placeholders
    test_list = [
        "aux_light_(SIDE)",
        "ENG[SIDE]",
        "MOTOR[ARM]",
        "no_placeholder"
    ]
    
    result = ph_data.get_placeholders(test_list)
    print(f"  List test:")
    print(f"    Combined sets: {result.combined_phs.sets}")
    print(f"    Combined functions: {result.combined_phs.funs}")
    print(f"    Combined relations: {result.combined_phs.rels}")
    
    # Test individual item placeholders
    for i, item in enumerate(test_list):
        print(f"    Item {i} '{item}': {result.item_phs[i].sets}")

def test_PlaceHoldersInStr():
    """Test PlaceHoldersInStr class"""
    print("\nTesting PlaceHoldersInStr class...")
    
    # Test with string containing placeholders
    test_str = "aux_light_(SIDE)_ENG[SIDE]_MOTOR[ARM]"
    ph_str = PlaceHoldersInStr(test_str)
    
    print(f"  Data: {ph_str.data}")
    print(f"  Sets: {ph_str.sets}")
    print(f"  Functions: {ph_str.funs}")
    print(f"  Relations: {ph_str.rels}")
    
    # Test with None
    ph_none = PlaceHoldersInStr(None)
    print(f"  None data: {ph_none.data}")

def test_PlaceHoldersInDict():
    """Test PlaceHoldersInDict class"""
    print("\nTesting PlaceHoldersInDict class...")
    
    # Test dictionary with placeholders
    test_dict = {
        "aux_light_(SIDE)": "ENG[SIDE]",
        "rtk_cable_(SIDE)": "SPA[SIDE]",
        "m(ARM)_esc_cable": "MOTOR[ARM]"
    }
    
    ph_dict = PlaceHoldersInDict(test_dict)
    
    print(f"  Data keys: {list(ph_dict.data.keys())}")
    print(f"  Leads to dict: {ph_dict.leads_to_dict}")
    print(f"  Leads to list: {ph_dict.leads_to_list}")
    
    # Test with nested structures
    nested_dict = {
        "simple_key": "simple_value",
        "nested_dict": {"inner": "value"},
        "nested_list": ["item1", "item2"]
    }
    
    ph_nested = PlaceHoldersInDict(nested_dict)
    print(f"  Nested leads to dict: {ph_nested.leads_to_dict}")
    print(f"  Nested leads to list: {ph_nested.leads_to_list}")

def test_PlaceHoldersInList():
    """Test PlaceHoldersInList class"""
    print("\nTesting PlaceHoldersInList class...")
    
    # Test list with placeholders
    test_list = [
        "aux_light_(SIDE)",
        "ENG[SIDE]",
        "MOTOR[ARM]"
    ]
    
    ph_list = PlaceHoldersInList(test_list)
    
    print(f"  Data length: {len(ph_list.data)}")
    print(f"  Leads to dict: {ph_list.leads_to_dict}")
    print(f"  Leads to list: {ph_list.leads_to_list}")
    
    # Test with nested structures
    nested_list = [
        "simple_item",
        {"nested": "dict"},
        ["nested", "list"]
    ]
    
    ph_nested = PlaceHoldersInList(nested_list)
    print(f"  Nested leads to dict: {ph_nested.leads_to_dict}")
    print(f"  Nested leads to list: {ph_nested.leads_to_list}")

def test_with_test_files():
    """Test data structures with actual test JSON files"""
    print("\nTesting with actual test files...")
    
    # Test loading test files
    test1_path = Path("newlang/test1.json")
    test2_path = Path("newlang/test2.json")
    
    if test1_path.exists():
        test1_data = load_json_file(str(test1_path))
        print(f"  ✓ test1.json loaded successfully")
        
        # Test placeholder extraction from test1.json
        test1_str = json.dumps(test1_data)
        ph_data = load_placeholders()
        result = ph_data.get_placeholders(test1_str)
        
        print(f"    Placeholders found in test1.json:")
        print(f"      Sets: {result.sets}")
        print(f"      Functions: {result.funs}")
        print(f"      Relations: {result.rels}")
    
    if test2_path.exists():
        test2_data = load_json_file(str(test2_path))
        print(f"  ✓ test2.json loaded successfully")
        
        # Test placeholder extraction from test2.json
        test2_str = json.dumps(test2_data)
        ph_data = load_placeholders()
        result = ph_data.get_placeholders(test2_str)
        
        print(f"    Placeholders found in test2.json:")
        print(f"      Sets: {result.sets}")
        print(f"      Functions: {result.funs}")
        print(f"      Relations: {result.rels}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing data_structures.py")
    print("=" * 60)
    
    try:
        test_load_placeholders()
        test_PlaceHolderDatabase_class()
        test_get_placeholder_sets()
        test_get_placeholder_funs()
        test_get_placeholder_rels()
        test_get_placeholders_string()
        test_get_placeholders_dict()
        test_get_placeholders_list()
        test_PlaceHoldersInStr()
        test_PlaceHoldersInDict()
        test_PlaceHoldersInList()
        test_with_test_files()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
