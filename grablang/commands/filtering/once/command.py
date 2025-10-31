"""
Commande FILTER ONCE pour filtrer et retourner un élément spécifique par index
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import re

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class FilteringOnceCommand(BaseCommand):
    """Commande pour filtrer et retourner un élément spécifique par index parmi ceux qui correspondent à une condition WHERE"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("FILTER ONCE", "FILTER")
            print(f"{colored_prefix} {message}")
    
    def _matches_condition(self, element: Tag, condition_args: List[str]) -> bool:
        """Vérifie si un élément correspond à une condition"""
        if len(condition_args) < 3:
            return False
        
        field = condition_args[0].lower()
        operator = condition_args[1].upper()
        value = condition_args[2]
        
        # Récupère la valeur à tester selon le champ
        if field == "class":
            test_value = " ".join(element.get("class", []))
        elif field == "text":
            test_value = element.get_text(strip=True)
        elif field == "attr":
            if len(condition_args) < 4:
                return False
            attr_name = condition_args[2]
            operator = condition_args[3].upper()
            value = condition_args[4] if len(condition_args) > 4 else None
            test_value = element.get(attr_name)
        else:
            # Assume it's an attribute name
            test_value = element.get(field)
        
        # Applique l'opérateur
        if operator == "CONTAINS":
            return value.lower() in str(test_value).lower() if test_value else False
        elif operator == "MATCHES":
            return bool(re.search(value, str(test_value))) if test_value else False
        elif operator == "NOT" and len(condition_args) > 3 and condition_args[3].upper() == "NULL":
            return test_value is not None
        elif operator == "NULL":
            return test_value is None
        elif operator == "=":
            return str(test_value) == value if test_value else False
        elif operator == "!=":
            return str(test_value) != value if test_value else True
        
        return False
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Optional[Tag]:
        """
        Exécute FILTER ONCE index WHERE condition
        
        Args:
            args: [index, WHERE, condition_args...] où index est 1-based et condition_args sont les critères de filtrage
            variables: Variables disponibles
            
        Returns:
            Tag contenant l'élément à l'index spécifié parmi ceux qui correspondent à la condition
        """
        if len(args) < 4:
            raise ValueError("FILTER ONCE: Syntaxe incorrecte. Utilisez: FILTER ONCE index WHERE condition")
        
        # Premier argument est l'index
        try:
            target_index = int(args[0])
        except ValueError:
            raise ValueError(f"FILTER ONCE: L'index doit être un nombre entier, reçu '{args[0]}'")
        
        if target_index < 1:
            raise ValueError(f"FILTER ONCE: L'index doit être supérieur à 0, reçu {target_index}")
        
        # Vérifie que WHERE est présent
        if args[1].upper() != "WHERE":
            raise ValueError("FILTER ONCE: Syntaxe incorrecte. Le mot 'WHERE' est requis après l'index")
        
        # Les arguments de condition commencent après WHERE
        condition_args = args[2:]
        
        if len(condition_args) < 3:
            raise ValueError("FILTER ONCE: Condition incomplète après WHERE")
        
        # Récupère les éléments à filtrer
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("FILTER ONCE: Aucun élément à filtrer")
        
        elements_to_filter = []
        if isinstance(last_result, ResultSet):
            elements_to_filter = list(last_result)
        elif isinstance(last_result, Tag):
            elements_to_filter = [last_result]
        else:
            raise ValueError("FILTER ONCE: Les données à filtrer doivent être des éléments HTML")
        
        self._debug_print(f"Recherche de l'élément à l'index {target_index} parmi ceux correspondant à: {' '.join(condition_args)}")
        
        # Collecte tous les éléments qui correspondent à la condition
        matching_elements = []
        for element in elements_to_filter:
            if self._matches_condition(element, condition_args):
                matching_elements.append(element)
        
        self._debug_print(f"{len(matching_elements)} élément(s) correspondent à la condition")
        
        if len(matching_elements) == 0:
            raise ValueError(f"FILTER ONCE: Aucun élément ne correspond à la condition: {' '.join(args)}")
        
        if len(matching_elements) == 1:
            target_index = 0
        else:
            target_index = target_index - 1  # Convert to 0-based
        
        self._debug_print(f"Élément à l'index {target_index} sélectionné")
        
        # Vérifie que l'index existe (conversion 1-based vers 0-based)
        if target_index >= len(matching_elements):
            raise ValueError(f"FILTER ONCE: Index {target_index + 1} trop élevé. Il y a seulement {len(matching_elements)} élément(s) correspondant à la condition")
        
        selected_element = matching_elements[target_index]
        
        if self.debug_mode:
            preview = str(selected_element)[:200] + "..." if len(str(selected_element)) > 200 else str(selected_element)
            self._debug_print(f"  Élément: {preview}")
        
        return selected_element