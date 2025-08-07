#!/usr/bin/env python3
"""
Auxiliary Parsing functions
"""

def has_valid_words( cause : dict, valid_words : list[str]) -> bool :
    for word in valid_words:
        if any( str(key).startswith(word) for key in cause.keys() ) :
            return True
    return False

def has_valid_cause_keys( cause : dict) -> bool :
    # Cause must have either a component or a problem
    valid_words = [ 'component', 'problem']
    cond_1 = has_valid_words( cause, valid_words)
    # Cause must have a probability or frequency
    valid_words = [ 'probability', 'frequency' ]
    cond_2 = has_valid_words( cause, valid_words)
    # Enforce conditions
    return cond_1 and cond_2
