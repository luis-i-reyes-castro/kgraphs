#!/usr/bin/env python3
"""
Count tokens in JSON files
"""

import os
import sys
import tiktoken
from utilities_io import load_file_as_string
from utilities_printing import print_sep

def count_tokens_in_string( string : str, encoding_name : str = "cl100k_base") -> int :
    """Returns the number of tokens in a text string."""
    encoding   = tiktoken.get_encoding(encoding_name)
    num_tokens = len( encoding.encode(string) )
    return num_tokens

def analyze_json_files( directory : str) -> dict :
    """
    Analyzes all JSON files in the given directory and returns token counts.
    Returns a dictionary with filenames as keys and token counts as values.
    """
    token_counts = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join( directory, filename)
            try:
                content_string = load_file_as_string(filepath)
                token_counts[filename] = count_tokens_in_string(content_string)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    return token_counts

if __name__ == "__main__" :
    # Analyze current directory unless a directory is specified
    directory = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    # Analyze files
    token_counts = analyze_json_files(directory)
    # Print token counts for each file (sorted alphabetically)
    print_sep()
    print("Token counts per file:")
    print_sep()
    total_tokens = 0
    for filename, count in sorted(token_counts.items()) :
        print(f"{filename:<40}{count:>8} tokens")
        total_tokens += count
    print_sep()
    # Print total token count
    msg = "Total tokens across all files:"
    print(f"{msg:<40}{total_tokens:>8}")
    print_sep()
