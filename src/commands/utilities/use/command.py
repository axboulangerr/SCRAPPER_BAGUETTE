"""
Commande USE pour réutiliser le contenu d'une variable comme _last_result
"""
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

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
        
        # Si c'est un document HTML complet, met à jour _original_html
        if hasattr(variable_content, 'find') and variable_content.name is None:  # BeautifulSoup root
            variables['_original_html'] = variable_content
            self._debug_print(f"Variable '{variable_name}' définie comme document HTML principal")
        # Si c'est un élément HTML spécifique, garde le document original
        elif '_original_html' in variables:
            self._debug_print(f"Variable '{variable_name}' utilisée, document HTML principal préservé")
        
        result_type = type(variable_content).__name__
        self._debug_print(f"Variable '{variable_name}' réutilisée (type: {result_type})")
        
        return variable_content