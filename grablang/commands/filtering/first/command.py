"""
Commande FILTER FIRST pour filtrer et retourner le premier élément correspondant
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

class FilteringFirstCommand(BaseCommand):
    """Commande pour filtrer et retourner le premier élément correspondant à une condition WHERE"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("FILTER FIRST", "FILTER")
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
        Exécute FILTER FIRST WHERE condition
        
        Args:
            args: condition arguments (ex: ["class", "CONTAINS", "active"])
            variables: Variables disponibles
            
        Returns:
            Tag contenant le premier élément qui correspond à la condition, ou None
        """
        if len(args) < 3:
            raise ValueError("FILTER FIRST: Condition incomplète. Exemples: class CONTAINS \"active\", text MATCHES \"^[0-9]+$\"")
        
        # Récupère les éléments à filtrer
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("FILTER FIRST: Aucun élément à filtrer")
        
        elements_to_filter = []
        if isinstance(last_result, ResultSet):
            elements_to_filter = list(last_result)
        elif isinstance(last_result, Tag):
            elements_to_filter = [last_result]
        else:
            raise ValueError("FILTER FIRST: Les données à filtrer doivent être des éléments HTML")
        
        self._debug_print(f"Recherche du premier élément correspondant parmi {len(elements_to_filter)} élément(s) avec condition: {' '.join(args)}")
        
        # Cherche le premier élément correspondant
        for i, element in enumerate(elements_to_filter):
            if self._matches_condition(element, args):
                self._debug_print(f"Premier élément trouvé à l'index {i}")
                if self.debug_mode:
                    preview = str(element)[:200] + "..." if len(str(element)) > 200 else str(element)
                    self._debug_print(f"  Élément: {preview}")
                return element
        
        raise ValueError(f"FILTER FIRST: Aucun élément ne correspond à la condition: {' '.join(args)}")