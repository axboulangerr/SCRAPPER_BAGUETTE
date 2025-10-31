"""
Commande GET ATTR ONCE pour extraire l'attribut d'un élément spécifique par son index
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterAttrOnceCommand(BaseCommand):
    """Commande pour extraire l'attribut d'un élément spécifique par son index"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET ATTR ONCE", "GET ATTR")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Optional[str]:
        """
        Exécute GET ATTR ONCE "tag" index "attribute"
        
        Args:
            args: [tag, index, attribute] - Le type d'élément, l'index (1-based) et l'attribut à extraire
            variables: Variables disponibles
            
        Returns:
            str contenant la valeur de l'attribut de l'élément à l'index spécifié
        """
        self.validate_args(args, 3, "GET ATTR ONCE")
        
        tag = args[0]
        try:
            index = int(args[1])
        except ValueError:
            raise ValueError(f"GET ATTR ONCE: L'index doit être un nombre entier, reçu '{args[1]}'")
        
        if index < 1:
            raise ValueError(f"GET ATTR ONCE: L'index doit être supérieur à 0, reçu {index}")
        
        attribute_name = args[2]
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET ATTR ONCE: Aucun contenu HTML disponible")
        
        self._debug_print(f"Recherche de l'élément '{tag}' à l'index {index} pour extraire l'attribut '{attribute_name}'")
        
        # Trouve tous les éléments du type spécifié
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"GET ATTR ONCE: Aucun élément '{tag}' trouvé")
        
        # Vérifie que l'index existe (conversion 1-based vers 0-based)
        if index > len(elements):
            raise ValueError(f"GET ATTR ONCE: Index {index} trop élevé. Il y a seulement {len(elements)} élément(s) '{tag}'")
        
        selected_element = elements[index - 1]  # Conversion 1-based vers 0-based
        
        # Extrait l'attribut
        attr_value = selected_element.get(attribute_name)
        if attr_value is None:
            self._debug_print(f"⚠️ Attribut '{attribute_name}' non trouvé dans l'élément '{tag}' à l'index {index}")
            return None
        
        # Gère les attributs multiples (comme class)
        if isinstance(attr_value, list):
            attr_value = " ".join(attr_value)
        
        self._debug_print(f"Attribut '{attribute_name}' de l'élément '{tag}' à l'index {index} (parmi {len(elements)} éléments): {attr_value}")
        
        return attr_value