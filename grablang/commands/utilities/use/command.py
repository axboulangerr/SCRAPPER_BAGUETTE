"""
Commande USE pour récupérer une variable et la mettre dans _last_result
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any
import sys
from pathlib import Path

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class UtilitiesUseCommand(BaseCommand):
    """Commande pour réutiliser le contenu d'une variable et la définir comme _last_result"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("USE", "SAVE")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """
        Exécute USE variable_name
        
        Args:
            args: [variable_name] - Le nom de la variable à réutiliser
            variables: Variables disponibles
            
        Returns:
            Le contenu de la variable réutilisée
        """
        self.validate_args(args, 1, "USE")
        
        variable_name = args[0]
        
        if variable_name not in variables:
            available_vars = [var for var in variables.keys() if not var.startswith('_')]
            if available_vars:
                available_str = ", ".join(available_vars)
                raise ValueError(f"USE: Variable '{variable_name}' non trouvée. Variables disponibles: {available_str}")
            else:
                raise ValueError(f"USE: Variable '{variable_name}' non trouvée. Aucune variable sauvegardée.")
        
        # Récupère le contenu de la variable
        variable_content = variables[variable_name]
        
        # Met à jour _last_result avec le contenu de la variable
        variables['_last_result'] = variable_content
        
        # Si c'est un document HTML complet (BeautifulSoup), met à jour _original_html
        if isinstance(variable_content, BeautifulSoup):
            variables['_original_html'] = variable_content
            self._debug_print(f"Variable '{variable_name}' définie comme document HTML principal")
        # Sinon, vérifie si on a besoin de garder le document original
        elif '_original_html' not in variables:
            # Si aucun document original n'est défini, essaie de trouver un document parent
            # depuis les autres variables BeautifulSoup disponibles
            for var_name, var_content in variables.items():
                if isinstance(var_content, BeautifulSoup) and not var_name.startswith('_'):
                    variables['_original_html'] = var_content
                    self._debug_print(f"Document HTML principal restauré depuis '{var_name}'")
                    break
        
        result_type = type(variable_content).__name__
        
        # Message informatif selon le type
        if isinstance(variable_content, BeautifulSoup):
            colored_prefix = CommandColors.colorize_prefix("USE", "SAVE")
            print(f"{colored_prefix} Variable '{variable_name}' réutilisée (type: {result_type})")
        else:
            self._debug_print(f"Variable '{variable_name}' réutilisée (type: {result_type})")
        
        return variable_content