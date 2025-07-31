#!/usr/bin/env python3
"""
Test script for expand.py
"""

from expand import expand_value
from utilities import load_placeholders, placeholderData

def test_expand_value():
    """Test the expand_value function with various scenarios"""
    print("Testing expand_value function...")
    
    # Load placeholders
    base_ph_data = load_placeholders()
    
    # Test 1: Simple set placeholder
    print("\nTest 1: Simple set placeholder")
    ph_data = placeholderData(set_map={"SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("cable_(SIDE)", ph_data)
    print(f"  Input: 'cable_(SIDE)' with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result == "cable_l"
    
    # Test 2: Function call
    print("\nTest 2: Function call")
    ph_data = placeholderData(set_map={"SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("light_(ENG[SIDE])", ph_data)
    print(f"  Input: 'light_(ENG[SIDE])' with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result == "light_Left"
    
    # Test 3: Relation (set-returning function)
    print("\nTest 3: Relation (set-returning function)")
    ph_data = placeholderData(set_map={"ARM": "1"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("motor_(*MOTOR[ARM])", ph_data)
    print(f"  Input: 'motor_(*MOTOR[ARM])' with set_context={{'ARM': '1'}}")
    print(f"  Result: {result}")
    assert isinstance(result, list)
    assert "motor_1" in result
    assert "motor_5" in result
    
    # Test 4: Mixed placeholders
    print("\nTest 4: Mixed placeholders")
    ph_data = placeholderData(set_map={"SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("aux_light_(SIDE)_(ENG[SIDE])", ph_data)
    print(f"  Input: 'aux_light_(SIDE)_(ENG[SIDE])' with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result == "aux_light_l_Left"
    
    # Test 5: Nested structure
    print("\nTest 5: Nested structure")
    ph_data = placeholderData(set_map={"SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    input_dict = {"name": "light_(SIDE)", "type": "auxiliary"}
    result = expand_value(input_dict, ph_data)
    print(f"  Input: {input_dict} with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result["name"] == "light_l"
    assert result["type"] == "auxiliary"
    
    # Test 6: List with relations
    print("\nTest 6: List with relations")
    ph_data = placeholderData(set_map={"ARM": "1", "SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    input_list = ["motor_(*MOTOR[ARM])", "cable_(SIDE)"]
    result = expand_value(input_list, ph_data)
    print(f"  Input: {input_list} with set_context={{'ARM': '1', 'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], list)  # First element should be a list due to relation
    assert isinstance(result[1], str)   # Second element should be a string
    
    # Test 7: No placeholders
    print("\nTest 7: No placeholders")
    ph_data = placeholderData(set_map={"SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("simple_text", ph_data)
    print(f"  Input: 'simple_text' with set_context={{'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert result == "simple_text"
    
    # Test 8: Multiple relations
    print("\nTest 8: Multiple relations")
    ph_data = placeholderData(set_map={"ARM": "1", "SIDE": "l"}, fun_map=base_ph_data.fun_map, rel_map=base_ph_data.rel_map)
    ph_data.process_aux_objs()
    result = expand_value("motor_(*MOTOR[ARM])_(SIDE)", ph_data)
    print(f"  Input: 'motor_(*MOTOR[ARM])_(SIDE)' with set_context={{'ARM': '1', 'SIDE': 'l'}}")
    print(f"  Result: {result}")
    assert isinstance(result, list)
    assert "motor_1_l" in result
    assert "motor_5_l" in result
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_expand_value()
