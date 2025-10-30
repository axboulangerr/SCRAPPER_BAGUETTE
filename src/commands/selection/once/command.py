"""
Commande SELECT ONCE pour récupérer un élément spécifique par son index
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class SelectOnceCommand(BaseCommand):
    """Commande pour sélectionner un élément spécifique par son index"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("SELECT ONCE", "SELECT ONCE")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Tag:
        """
        Exécute SELECT ONCE "tag" index
        
        Args:
            args: [tag, index] - Le tag HTML à rechercher et l'index (1-based)
            variables: Variables disponibles
            
        Returns:
            Tag contenant l'élément à l'index spécifié
        """
        self.validate_args(args, 2, "SELECT ONCE")
        
        tag = args[0]
        try:
            index = int(args[1])
        except ValueError:
            raise ValueError(f"SELECT ONCE: L'index doit être un nombre entier, reçu '{args[1]}'")
        
        if index < 1:
            raise ValueError(f"SELECT ONCE: L'index doit être supérieur à 0, reçu {index}")
        
        soup = variables['_current_soup']
        
        if not isinstance(soup, BeautifulSoup):
            raise ValueError("SELECT ONCE: Le contenu chargé n'est pas un document HTML valide")
        
        self._debug_print(f"Recherche de l'élément '{tag}' à l'index {index}")
        
        # Utilise find_all pour récupérer tous les éléments
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"SELECT ONCE: Aucun élément '{tag}' trouvé")
        
        # Vérifie que l'index existe (conversion 1-based vers 0-based)
        if index > len(elements):
            raise ValueError(f"SELECT ONCE: Index {index} trop élevé. Il y a seulement {len(elements)} élément(s) '{tag}'")
        
        selected_element = elements[index - 1]  # Conversion 1-based vers 0-based
        
        self._debug_print(f" Élément '{tag}' à l'index {index} trouvé (parmi {len(elements)} éléments)")
        
        return selected_element