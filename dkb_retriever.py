#!/usr/bin/env python3
"""
Domain Knowledge Retriever
"""

from abc_project_vars import DIR_DKNOWLEDGE_B
from utilities_dkb import load_domain_knowledge

class DomainKnowledgeRetriever :
    
    def __init__( self, language : str = 'English') -> None :
        
        self.data = load_domain_knowledge(DIR_DKNOWLEDGE_B)
        
        if language not in ( 'English', 'Spanish') :
            raise ValueError( f"Invalid language: {language}")
        self.lang = language
        
        self.dict_error_names = {}
        self.list_error_names = []
        self.build_dict_list_error_names()
        
        return
    
    def build_dict_list_error_names(self) -> None :
        # Inner key of name depends on the language
        inner_key_of_name = ''
        match self.lang :
            case 'English' :
                inner_key_of_name += 'name'
            case 'Spanish' :
                inner_key_of_name += 'name_spanish'
        
        # Build dict mapping error names to error codes
        for outer_key, inner_dict in self.data['errors'].items() :
            error_name = inner_dict[inner_key_of_name]
            self.dict_error_names[error_name] = outer_key
        
        # Build list of error names
        self.list_error_names = self.dict_error_names.keys()
        
        return
