#!/usr/bin/env python3
"""
Publishes lists of errors as Markdown file to directory of agent prompts
"""

import os
from abc_project_vars import DIR_AGENT_PROMPTS
from dkb_retriever import DomainKnowledgeRetriever
from utilities_io import save_to_file

if __name__ == '__main__' :
    
    output_str   = f'## List of Most Common Errors\n\n'
    output_path  = os.path.join( DIR_AGENT_PROMPTS, 'list_error_names.md')
    retriever    = DomainKnowledgeRetriever('English')
    list_e_names = retriever.list_error_names
    for e_name in list_e_names :
        output_str += f'* {e_name}\n'
    
    save_to_file( output_str, output_path)
