"""
Commande GET ATTR LAST pour extraire l'attribut du dernier élément d'un type donné
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterAttrLastCommand(BaseCommand):
    """Commande pour extraire l'attribut du dernier élément d'un type donné"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET ATTR LAST", "GET ATTR")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Optional[str]:
        """
        Exécute GET ATTR LAST "tag" "attribute"
        
        Args:
            args: [tag, attribute] - Le type d'élément et l'attribut à extraire
            variables: Variables disponibles
            
        Returns:
            str contenant la valeur de l'attribut du dernier élément trouvé
        """
        self.validate_args(args, 2, "GET ATTR LAST")
        
        tag = args[0]
        attribute_name = args[1]
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET ATTR LAST: Aucun contenu HTML disponible")
        
        self._debug_print(f"Recherche du dernier élément '{tag}' pour extraire l'attribut '{attribute_name}'")
        
        # Trouve tous les éléments du type spécifié
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"GET ATTR LAST: Aucun élément '{tag}' trouvé")
        
        # Prend le dernier élément
        last_element = elements[-1]
        
        # Extrait l'attribut
        attr_value = last_element.get(attribute_name)
        if attr_value is None:
            self._debug_print(f"⚠️ Attribut '{attribute_name}' non trouvé dans le dernier élément '{tag}'")
            return None
        
        # Gère les attributs multiples (comme class)
        if isinstance(attr_value, list):
            attr_value = " ".join(attr_value)
        
        self._debug_print(f"Attribut '{attribute_name}' du dernier '{tag}' (parmi {len(elements)} éléments): {attr_value}")
        
        return attr_value