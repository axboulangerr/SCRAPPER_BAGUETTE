"""
Commande SAVE pour sauvegarder le contenu de _last_result dans une variable
"""
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class UtilitiesSaveCommand(BaseCommand):
    """Commande pour sauvegarder le dernier résultat dans une variable nommée"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("SAVE", "SAVE")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> None:
        """
        Exécute SAVE variable_name
        
        Args:
            args: [variable_name] - Le nom de la variable où sauvegarder
            variables: Variables disponibles
            
        Returns:
            None
        """
        self.validate_args(args, 1, "SAVE")
        
        variable_name = args[0]
        
        if '_last_result' not in variables:
            raise ValueError("SAVE: Aucun résultat à sauvegarder. Exécutez d'abord une commande qui produit un résultat.")
        
        # Sauvegarde le dernier résultat dans la variable nommée
        variables[variable_name] = variables['_last_result']
        
        result_type = type(variables['_last_result']).__name__
        self._debug_print(f"Variable '{variable_name}' sauvegardée (type: {result_type})")
        
        return None