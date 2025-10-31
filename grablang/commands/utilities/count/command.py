"""
Commande COUNT pour compter le nombre d'éléments dans une variable
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import sys
from pathlib import Path

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class UtilitiesCountCommand(BaseCommand):
    """Commande pour compter le nombre d'éléments dans une variable"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("COUNT", "COUNT")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> int:
        """
        Exécute COUNT variable_name ou COUNT (pour _last_result)
        
        Args:
            args: [variable_name] optionnel - La variable à compter
            variables: Variables disponibles
            
        Returns:
            int - Le nombre d'éléments
        """
        if len(args) == 0:
            # COUNT sans argument : compte _last_result
            if '_last_result' not in variables:
                raise ValueError("COUNT: Aucun résultat précédent à compter")
            
            target = variables['_last_result']
            var_name = "_last_result"
        
        elif len(args) == 1:
            # COUNT variable_name
            var_name = args[0]
            if var_name not in variables:
                available_vars = [name for name in variables.keys() if not name.startswith('_')]
                if available_vars:
                    available_str = ", ".join(available_vars)
                    raise ValueError(f"COUNT: Variable '{var_name}' non trouvée. Variables disponibles: {available_str}")
                else:
                    raise ValueError(f"COUNT: Variable '{var_name}' non trouvée. Aucune variable disponible.")
            
            target = variables[var_name]
        
        else:
            raise ValueError("COUNT: Trop d'arguments. Utilisez COUNT ou COUNT variable_name")
        
        # Compte selon le type de données
        count = self._count_elements(target)
        
        self._debug_print(f"Comptage de '{var_name}': {count} élément(s)")
        
        return count
    
    def _count_elements(self, data: Any) -> int:
        """Compte le nombre d'éléments selon le type de données"""
        
        if data is None:
            return 0
        
        # Types avec longueur définie
        if hasattr(data, '__len__'):
            return len(data)
        
        # Types spéciaux
        elif isinstance(data, (BeautifulSoup, Tag)):
            # Pour HTML, compte 1 (c'est un seul élément)
            return 1
        
        # Types scalaires
        elif isinstance(data, (str, int, float, bool)):
            return 1
        
        # Autres types itérables
        elif hasattr(data, '__iter__'):
            try:
                return len(list(data))
            except:
                return 1
        
        # Par défaut
        else:
            return 1