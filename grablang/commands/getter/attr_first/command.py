"""
Commande GET ATTR FIRST pour extraire l'attribut du premier élément d'un type donné
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterAttrFirstCommand(BaseCommand):
    """Commande pour extraire l'attribut du premier élément d'un type donné"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET ATTR FIRST", "GET ATTR")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Optional[str]:
        """
        Exécute GET ATTR FIRST "tag" "attribute"
        
        Args:
            args: [tag, attribute] - Le type d'élément et l'attribut à extraire
            variables: Variables disponibles
            
        Returns:
            str contenant la valeur de l'attribut du premier élément trouvé
        """
        self.validate_args(args, 2, "GET ATTR FIRST")
        
        tag = args[0]
        attribute_name = args[1]
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET ATTR FIRST: Aucun contenu HTML disponible")
        
        self._debug_print(f"Recherche du premier élément '{tag}' pour extraire l'attribut '{attribute_name}'")
        
        # Trouve le premier élément du type spécifié
        element = soup.find(tag)
        
        if element is None:
            raise ValueError(f"GET ATTR FIRST: Aucun élément '{tag}' trouvé")
        
        # Extrait l'attribut
        attr_value = element.get(attribute_name)
        if attr_value is None:
            self._debug_print(f"⚠️ Attribut '{attribute_name}' non trouvé dans le premier élément '{tag}'")
            return None
        
        # Gère les attributs multiples (comme class)
        if isinstance(attr_value, list):
            attr_value = " ".join(attr_value)
        
        self._debug_print(f"Attribut '{attribute_name}' du premier '{tag}': {attr_value}")
        
        return attr_value