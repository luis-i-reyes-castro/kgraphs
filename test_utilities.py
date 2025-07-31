#!/usr/bin/env python3
"""
Test script for utilities.py using test JSON files in newlang/
"""

import json
import sys
from pathlib import Path
from utilities import (
    load_json_file,
    isvalid_set,
    isvalid_fun,
    isvalid_rel,
)
from data_structures import PlaceHolderData, load_placeholders
import regex_constants as rxconst

def test_load_json_file():
    """Test load_json_file function"""
    print("Testing load_json_file...")
    
    # Test loading test1.json
    test1_path = Path("newlang/test1.json")
    if test1_path.exists():
        test1_data = load_json_file(str(test1_path))
        print(f"  ✓ Successfully loaded test1.json")
        print(f"    Keys: {list(test1_data.keys())}")
    else:
        print(f"  ✗ test1.json not found")
    
    # Test loading test2.json
    test2_path = Path("newlang/test2.json")
    if test2_path.exists():
        test2_data = load_json_file(str(test2_path))
        print(f"  ✓ Successfully loaded test2.json")
        print(f"    Keys: {list(test2_data.keys())}")
    else:
        print(f"  ✗ test2.json not found")

def test_isvalid_set():
    """Test isvalid_set function"""
    print("\nTesting isvalid_set...")
    
    # Valid sets
    valid_sets = [
        ["l", "r"],
        ["1", "2", "3", "4"],
        [1, 2, 3, 4],
        ["Left", "Right"]
    ]
    
    for i, test_set in enumerate(valid_sets):
        result = isvalid_set(test_set)
        print(f"  Test {i+1}: {test_set} -> {result}")
        assert result == True, f"Expected True for valid set {test_set}"
    
    # Invalid sets
    invalid_sets = [
        [],  # Empty set
        ["l", "r", 1],  # Mixed types
        None,  # None
        ["l"]  # Single element (should be valid)
    ]
    
    for i, test_set in enumerate(invalid_sets):
        if test_set is not None:
            result = isvalid_set(test_set)
            expected = len(test_set) > 0 and (len(test_set) == 1 or all(type(x) == type(test_set[0]) for x in test_set))
            print(f"  Test {i+1}: {test_set} -> {result} (expected: {expected})")
            assert result == expected, f"Unexpected result for set {test_set}"

def test_isvalid_fun():
    """Test isvalid_fun function"""
    print("\nTesting isvalid_fun...")
    
    # Create a simple set_map for testing
    set_map = {
        "SIDE": ["l", "r"],
        "ARM": ["1", "2", "3", "4"]
    }
    
    # Valid functions
    valid_functions = [
        ("ENG[SIDE]", {"l": "Left", "r": "Right"}),
        ("SPA[SIDE]", {"l": "Izquierda", "r": "Derecha"})
    ]
    
    for i, (sig, mapping) in enumerate(valid_functions):
        result = isvalid_fun(sig, mapping, set_map)
        print(f"  Test {i+1}: {sig} -> {result}")
        assert result == True, f"Expected True for valid function {sig}"
    
    # Invalid functions
    invalid_functions = [
        ("ENG[SIDE]", {"l": "Left"}),  # Missing key
        ("ENG[SIDE]", {"l": "Left", "r": "Right", "x": "Extra"}),  # Extra key
        ("ENG[INVALID]", {"l": "Left", "r": "Right"}),  # Invalid set name
        ("ENG[INVALID_SET]", {"l": "Left", "r": "Right"}),  # Invalid set name
    ]
    
    for i, (sig, mapping) in enumerate(invalid_functions):
        result = isvalid_fun(sig, mapping, set_map)
        print(f"  Test {i+1}: {sig} -> {result}")
        assert result == False, f"Expected False for invalid function {sig}"

def test_isvalid_rel():
    """Test isvalid_rel function"""
    print("\nTesting isvalid_rel...")
    
    # Create a simple set_map for testing
    set_map = {
        "ARM": ["1", "2", "3", "4"],
        "MOTOR": ["1", "2", "3", "4", "5", "6", "7", "8"]
    }
    
    # Valid relations
    valid_relations = [
        ("MOTOR[ARM]", {
            "1": ["1", "5"],
            "2": ["2", "6"],
            "3": ["3", "7"],
            "4": ["4", "8"]
        })
    ]
    
    for i, (sig, mapping) in enumerate(valid_relations):
        result = isvalid_rel(sig, mapping, set_map)
        print(f"  Test {i+1}: {sig} -> {result}")
        assert result == True, f"Expected True for valid relation {sig}"
    
    # Invalid relations
    invalid_relations = [
        ("MOTOR[INVALID_ARM]", {
            "1": ["1", "5"],
            "2": ["2", "6"]
        }),  # Invalid set name
        ("MOTOR[ARM]", {
            "1": ["1", "5"],
            "2": []  # Empty set
        }),  # Invalid set in relation
    ]
    
    for i, (sig, mapping) in enumerate(invalid_relations):
        result = isvalid_rel(sig, mapping, set_map)
        print(f"  Test {i+1}: {sig} -> {result}")
        assert result == False, f"Expected False for invalid relation {sig}"

def test_load_placeholders():
    """Test load_placeholders function"""
    print("\nTesting load_placeholders...")
    
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

def test_placeholderData_class():
    """Test placeholderData class"""
    print("\nTesting placeholderData class...")
    
    # Create test data
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    
    # Create placeholderData object
    ph_data = PlaceHolderData(set_map, func_map, rel_map)
    ph_data.process_aux_objs()
    
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

def test_get_placeholders():
    """Test get_placeholders method of placeholderData class"""
    print("\nTesting get_placeholders method...")
    
    # Test strings with placeholders
    test_strings = [
        "aux_light_(SIDE)",
        "ENG[SIDE]",
        "MOTOR[ARM]",
        "rtk_cable_(SIDE)",
        "m(ARM)_esc_cable",
        "esc_(*MOTOR[ARM])"
    ]
    
    # Create placeholderData object
    set_map = {"SIDE": ["l", "r"], "ARM": ["1", "2", "3", "4"]}
    func_map = {"ENG[SIDE]": {"l": "Left", "r": "Right"}}
    rel_map = {"MOTOR[ARM]": {"1": ["1", "5"], "2": ["2", "6"]}}
    ph_data = PlaceHolderData(set_map, func_map, rel_map)
    ph_data.process_aux_objs()
    
    for test_str in test_strings:
        ph_sets, ph_funs, ph_rels = ph_data.get_placeholders(test_str)
        print(f"  '{test_str}':")
        print(f"    Sets: {ph_sets}")
        print(f"    Functions: {ph_funs}")
        print(f"    Relations: {ph_rels}")

def test_with_test_files():
    """Test utilities with actual test JSON files"""
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
        ph_sets, ph_funs, ph_rels = ph_data.get_placeholders(test1_str)
        
        print(f"    Placeholders found in test1.json:")
        print(f"      Sets: {ph_sets}")
        print(f"      Functions: {ph_funs}")
        print(f"      Relations: {ph_rels}")
    
    if test2_path.exists():
        test2_data = load_json_file(str(test2_path))
        print(f"  ✓ test2.json loaded successfully")
        
        # Test placeholder extraction from test2.json
        test2_str = json.dumps(test2_data)
        ph_data = load_placeholders()
        ph_sets, ph_funs, ph_rels = ph_data.get_placeholders(test2_str)
        
        print(f"    Placeholders found in test2.json:")
        print(f"      Sets: {ph_sets}")
        print(f"      Functions: {ph_funs}")
        print(f"      Relations: {ph_rels}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing utilities.py")
    print("=" * 60)
    
    try:
        test_load_json_file()
        test_isvalid_set()
        test_isvalid_fun()
        test_isvalid_rel()
        test_load_placeholders()
        test_placeholderData_class()
        test_get_placeholders()
        test_with_test_files()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
