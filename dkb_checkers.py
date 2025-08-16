#!/usr/bin/env python3
"""
Parsing functions for placeholder substitution
"""

import os
from abc_project_vars import DIR_DKB as dir_input
from collections import OrderedDict
from utilities_io import load_json_file
from utilities_io import list_files_starting_with
from utilities_printing import print_ind

def check_components( data : OrderedDict) -> None :
    for comp_key, comp_dict in data.items() :
        if not 'type' in comp_dict :
            print_ind( f'⚠️ Component {comp_key} has no type', 1)
        if not 'name' in comp_dict :
            print_ind( f'⚠️ Component {comp_key} has no name', 1)
        if not 'name_spanish' in comp_dict :
            print_ind( f'⚠️ Component {comp_key} has no name_spanish', 1)
        if not 'material_num' in comp_dict :
            print_ind( f'⚠️ Component {comp_key} has no material_num', 1)
        if not 'material_name' in comp_dict :
            print_ind( f'⚠️ Component {comp_key} has no material_name', 1)
        if 'note' in comp_dict :
            print_ind( f'📝 Problem {message_key} has a note', 1)
        elif 'notes' in comp_dict :
            print_ind( f'📝 Problem {message_key} has a notes list', 1)
    return

def check_problems( data : OrderedDict) -> None :
    for prob_key, prob_dict in data.items() :
        if not 'name' in prob_dict :
            print_ind( f'⚠️ Problem {prob_key} has no name', 1)
        if not 'solutions' in prob_dict :
            print_ind( f'⚠️ Problem {prob_key} has no solutions list', 1)
        elif len(prob_dict['solutions']) == 0 :
            print_ind( f'⚠️ Problem {prob_key} has solutions list of length zero', 1)
        if 'note' in prob_dict :
            print_ind( f'📝 Problem {prob_key} has a note', 1)
        elif 'notes' in prob_dict :
            print_ind( f'📝 Problem {prob_key} has a notes list', 1)
    return

def check_signals( data : list, components : dict) -> set :
    
    signals_set = set()
    
    for i, item in enumerate(data) :
        if not 'signals' in item :
            print_ind( f'⚠️ Entry {i+1} does not have a \'signals\' key', 1)
        elif not isinstance( item['signals'], list) :
            print_ind( f'⚠️ Entry {i+1}: Key \'signals\' is not a list', 1)
        elif len(item['signals']) == 0 :
            print_ind( f'⚠️ Entry {i+1}: List \'signals\' has length zero', 1)
        else :
            for signal_item in item['signals'] :
                if signal_item in signals_set :
                    print_ind( f'⚠️ Entry {i+1} has a repeated signal: {signal_item}', 1)
                else :
                    signals_set.add(signal_item)
        
        if not 'path' in item :
            print_ind( f'⚠️ Entry {i+1} does not have a \'path\' key', 1)
        elif not isinstance( item['path'], list) :
            print_ind( f'⚠️ Entry {i+1}: Key \'path\' is not a list', 1)
        elif len(item['path']) == 0 :
            print_ind( f'⚠️ Entry {i+1}: List \'path\' has length zero', 1)
        else :
            for path_item in item['path'] :
                if path_item not in components :
                    msg = f'⚠️ Entry {i+1}: Path item {path_item} is not a component'
                    print_ind( msg, 1)
    
    return signals_set

def check_messages( data : OrderedDict,
                    components : OrderedDict,
                    problems : OrderedDict,
                    signals : set ) -> None :
    
    for msg_key, msg_dict in data.items() :
        # Check keys: name, name_spanish, causes
        if not 'name' in msg_dict :
            print_ind( f'⚠️ Message {msg_key} has no name', 1)
        if not 'name_spanish' in msg_dict :
            print_ind( f'⚠️ Message {msg_key} has no name_spanish', 1)
        
        # Check key: causes
        if str(msg_key).startswith(('ribbon_','warning_')) :
            continue
        if not 'causes' in msg_dict :
            print_ind( f'⚠️ Message {msg_key} has no causes', 1)
        elif not isinstance( msg_dict['causes'], dict) :
            print_ind( f'⚠️ Message {msg_key} has causes that are not a dict', 1)
        
        else:
            # Check causes dict
            causes = msg_dict['causes']
            # Check correctness of components
            if not 'components' in causes :
                print_ind( f'⚠️ Message {msg_key}, in \'causes\': no component key', 1)
            elif not isinstance( causes['components'], list) :
                print_ind( f'⚠️ Message {msg_key}, in \'causes[\'components\']\': components is not a list', 1)
            else :
                for comp_key in causes['components'] :
                    if comp_key not in components :
                        print_ind( f'⚠️ Message {msg_key}, in \'causes[\'components\']\': invalid component: {comp_key}', 1)
            # Check correctness of problems
            if not 'problems' in causes :
                print_ind( f'⚠️ Message {msg_key}, in \'causes\': no problems key', 1)
            elif not isinstance( causes['problems'], list) :
                print_ind( f'⚠️ Message {msg_key}, in \'causes[\'problems\']\': problems is not a list', 1)
            else :
                for prob_key in causes['problems'] :
                    if prob_key not in problems :
                        print_ind( f'⚠️ Message {msg_key}, in \'causes[\'problems\']\': invalid problem: {prob_key}', 1)
            # Check correctness of signals
            if not 'signals' in causes :
                print_ind( f'⚠️ Message {msg_key} has no signals', 1)
            elif not isinstance( causes['signals'], list) :
                print_ind( f'⚠️ Message {msg_key}, in \'causes[\'signals\']\': signals is not a list', 1)
            else :
                for signal_key in causes['signals'] :
                    if signal_key not in signals :
                        print_ind( f'⚠️ Message {msg_key}, in \'causes[\'signals\']\': invalid signal: {signal_key}', 1)
    
    return

if __name__ == "__main__" :
    
    # dir_input = DIR_DKA
    print_ind(f'Checking domain knowledge in: {dir_input}')

    # Check components
    components = OrderedDict()
    filenames  = list_files_starting_with( dir_input, 'components_', 'json')
    print_ind(f'Checking components...')
    for filename in filenames :
        print_ind(f'Processing file: {filename}')
        data = load_json_file(filename)
        check_components(data)
        for comp_key in data :
            if comp_key in components :
                print_ind( f'⚠️ Found repeated component key: {comp_key}', 1)
        components.update(data)
    
    # Check problems
    problems  = OrderedDict()
    filenames = list_files_starting_with( dir_input, 'problems_', 'json')
    print_ind(f'Checking problems...')
    for filename in filenames :
        print_ind(f'Processing file: {filename}')
        data = load_json_file(filename)
        check_problems(data)
        for message_key in data :
            if message_key in problems :
                print_ind( f'⚠️ Found repeated problem key: {message_key}', 1)
        problems.update(data)
    
    # Check signals
    signals   = set()
    filenames = list_files_starting_with( dir_input, 'signals_', 'json')
    print_ind(f'Checking signals...')
    for filename in filenames :
        print_ind(f'Processing file: {filename}')
        data = load_json_file(filename)
        data_signals = check_signals( data, components)
        for sig in data_signals :
            if sig in signals :
                print_ind( f'⚠️ Found repeated signal: {sig}', 1)
        signals.update(data_signals)
    
    # Check messages
    messages  = OrderedDict()
    filenames = list_files_starting_with( dir_input, 'messages_', 'json')
    print_ind(f'Checking messages...')
    for filename in filenames :
        print_ind(f'Processing file: {filename}')
        data = load_json_file(filename)
        check_messages( data, components, problems, signals)
        for message_key in data :
            if message_key in messages :
                print_ind( f'⚠️ Found repeated message key: {message_key}', 1)
        messages.update(data)
