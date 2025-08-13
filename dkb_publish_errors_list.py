#!/usr/bin/env python3
"""
Publishes lists of errors as Markdown file to directory of agent prompts
"""

import os
from abc_project_vars import DIR_DKNOWLEDGE_B
from dkb_retriever import DomainKnowledgeRetriever
from utilities_io import save_to_file
from utilities_printing import print_ind

if __name__ == '__main__' :
    
    print_ind(f'Collecting all error messages from: {DIR_DKNOWLEDGE_B}')
    
    output_file = 'messages_all.md'
    output_path = os.path.join( DIR_DKNOWLEDGE_B, output_file)
    retriever   = DomainKnowledgeRetriever('English')
    list_errors = retriever.list_message_names
    
    output_str = f'## List of All Messages\n\n'
    for e_name in list_errors :
        output_str += f'* {e_name}\n'
    
    save_to_file( output_str, output_path)

    print_ind( f'Saved list of all messages to:', 1)
    print_ind( f'{output_path}', 1)
