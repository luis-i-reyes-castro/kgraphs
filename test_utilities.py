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
    extract_arg_set,
    replace_placeholder,
)

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

def test_extract_arg_set():
    """Test extract_arg_set function"""
    print("\nTesting extract_arg_set...")
    
    # Valid signatures
    valid_signatures = [
        ("ENG[SIDE]", "SIDE"),
        ("MOTOR[ARM]", "ARM"),
        ("SPA[SIDE]", "SIDE"),
        ("ESC[MOTOR]", "MOTOR")
    ]
    
    for i, (sig, expected) in enumerate(valid_signatures):
        result = extract_arg_set(sig)
        print(f"  Test {i+1}: {sig} -> {result} (expected: {expected})")
        assert result == expected, f"Expected {expected} for signature {sig}"
    
    # Invalid signatures
    invalid_signatures = [
        "ENG",  # No brackets
        "ENG[]",  # Empty brackets
        "ENG[SIDE",  # Missing closing bracket
        "",  # Empty string
        None  # None
    ]
    
    for i, sig in enumerate(invalid_signatures):
        if sig is not None:
            result = extract_arg_set(sig)
            print(f"  Test {i+1}: {sig} -> {result} (expected: None)")
            assert result is None, f"Expected None for invalid signature {sig}"
    
    # Test edge case where regex still matches
    edge_case = "ENG[SIDE]]"  # Extra closing bracket
    result = extract_arg_set(edge_case)
    print(f"  Edge case: {edge_case} -> {result} (regex matches first occurrence)")
    assert result == "SIDE", f"Expected 'SIDE' for edge case {edge_case}"

def test_replace_placeholder():
    """Test replace_placeholder function"""
    print("\nTesting replace_placeholder...")
    
    # Test cases
    test_cases = [
        ("aux_light_(SIDE)", "l", "SIDE", "aux_light_l"),
        ("rtk_cable_(SIDE)", "r", "SIDE", "rtk_cable_r"),
        ("m(ARM)_esc_cable", "1", "ARM", "m1_esc_cable"),
        ("esc_(MOTOR[ARM])", "1", "MOTOR[ARM]", "esc_1"),
        ("no_placeholder", "value", "PLACEHOLDER", "no_placeholder"),  # No placeholder to replace
        ("multiple_(SIDE)_(SIDE)", "l", "SIDE", "multiple_l_l"),  # Replaces all occurrences
    ]
    
    for i, (val_orig, val_new, sig, expected) in enumerate(test_cases):
        result = replace_placeholder(val_orig, val_new, sig)
        print(f"  Test {i+1}: '{val_orig}' with '{val_new}' for '{sig}' -> '{result}' (expected: '{expected}')")
        assert result == expected, f"Expected '{expected}' for replacement in '{val_orig}'"

def test_with_test_files():
    """Test utilities with actual test JSON files"""
    print("\nTesting with actual test files...")
    
    # Test loading test files
    test1_path = Path("newlang/test1.json")
    test2_path = Path("newlang/test2.json")
    
    if test1_path.exists():
        test1_data = load_json_file(str(test1_path))
        print(f"  ✓ test1.json loaded successfully")
        print(f"    Type: {type(test1_data)}")
        print(f"    Keys: {list(test1_data.keys())}")
    
    if test2_path.exists():
        test2_data = load_json_file(str(test2_path))
        print(f"  ✓ test2.json loaded successfully")
        print(f"    Type: {type(test2_data)}")
        print(f"    Keys: {list(test2_data.keys())}")

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
        test_extract_arg_set()
        test_replace_placeholder()
        test_with_test_files()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
