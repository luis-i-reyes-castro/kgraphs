#!/usr/bin/env python3
"""
Test script for SAME function in PlaceHolderDatabase
"""

from data_structures import PlaceHolderDatabase, load_placeholders

def test_same_function():
    """Test the SAME function with various scenarios"""
    print("Testing SAME function...")
    
    # Load placeholders
    base_ph_data = load_placeholders()
    
    # Test 1: Simple SAME function
    print("\nTest 1: Simple SAME function")
    ph_data = PlaceHolderDatabase(set_map=base_ph_data.set_map, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.update()
    set_context = {"SIDE": "l"}
    result = ph_data.apply_phs("cable_(SAME[SIDE])", set_context)
    print(f"  Input: 'cable_(SAME[SIDE])' with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result == "cable_l"
    
    # Test 2: SAME function with multiple uses
    print("\nTest 2: SAME function with multiple uses")
    set_context = {"SIDE": "l", "ARM": "1"}
    result = ph_data.apply_phs("motor_(SAME[ARM])_(SAME[SIDE])", set_context)
    print(f"  Input: 'motor_(SAME[ARM])_(SAME[SIDE])' with set_context={{'SIDE': 'l', 'ARM': '1'}}")
    print(f"  Result: {result}")
    assert result == "motor_1_l"
    
    # Test 3: SAME function with non-existent set
    print("\nTest 3: SAME function with non-existent set")
    result = ph_data.apply_phs("test_(SAME[NONEXISTENT])", set_context)
    print(f"  Input: 'test_(SAME[NONEXISTENT])' with set_context={{'SIDE': 'l', 'ARM': '1'}}")
    print(f"  Result: {result}")
    # Should remain unchanged since NONEXISTENT is not in set_context
    assert result == "test_(SAME[NONEXISTENT])"
    
    # Test 4: Check that SAME functions are in fun_map
    print("\nTest 4: Check that SAME functions are in fun_map")
    same_functions = [key for key in ph_data.fun_map.keys() if key.startswith("SAME[")]
    print(f"  SAME functions found: {same_functions}")
    assert len(same_functions) > 0
    assert "SAME[SIDE]" in same_functions
    assert "SAME[ARM]" in same_functions
    
    # Test 5: Test BuiltInFunction behavior directly
    print("\nTest 5: Test BuiltInFunction behavior directly")
    same_func = ph_data.fun_map["SAME[SIDE]"]
    result = same_func["l"]
    print(f"  Direct call: SAME[SIDE]['l'] = {result}")
    assert result == "l"
    
    print("\n✅ All SAME function tests passed!")

if __name__ == "__main__":
    test_same_function() 