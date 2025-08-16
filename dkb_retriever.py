#!/usr/bin/env python3
"""
Domain Knowledge Retriever
"""

from abc_project_vars import DIR_DKB
from utilities_dkb import load_domain_knowledge

class DomainKnowledgeRetriever :
    
    def __init__( self, language : str = 'English') -> None :
        
        self.data = load_domain_knowledge(DIR_DKB)
        
        if language not in ( 'English', 'Spanish') :
            raise ValueError( f"Invalid language: {language}")
        self.lang = language
        
        self.dict_message_names = {}
        self.list_message_names = []
        self.build_dict_list_message_names()
        
        return
    
    def build_dict_list_message_names(self) -> None :
        # Message name field depends on the language
        message_name_field = ''
        match self.lang :
            case 'English' :
                message_name_field += 'name'
            case 'Spanish' :
                message_name_field += 'name_spanish'
        
        # Build dict mapping message names to message keys
        for message_key, inner_dict in self.data['messages'].items() :
            message_name = inner_dict[message_name_field]
            self.dict_message_names[message_name] = message_key
        
        # Build list of message names
        self.list_message_names = self.dict_message_names.keys()
        
        return
