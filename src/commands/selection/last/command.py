"""
Commande SELECT LAST pour récupérer le dernier élément correspondant à un sélecteur
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand

class SelectLastCommand(BaseCommand):
    """Commande pour sélectionner le dernier élément correspondant à un tag"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug"""
        if self.debug_mode:
            print(f"[SELECT LAST] {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Tag:
        """
        Exécute SELECT LAST "tag"
        
        Args:
            args: [tag] - Le tag HTML à rechercher
            variables: Variables disponibles
            
        Returns:
            Tag contenant le dernier élément trouvé
        """
        self.validate_args(args, 1, "SELECT LAST")
        
        tag = args[0]
        soup = variables['_current_soup']
        
        if not isinstance(soup, BeautifulSoup):
            raise ValueError("SELECT LAST: Le contenu chargé n'est pas un document HTML valide")
        
        self._debug_print(f"Recherche du dernier élément '{tag}'")
        
        # Utilise find_all pour récupérer tous les éléments puis prend le dernier
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"SELECT LAST: Aucun élément '{tag}' trouvé")
        
        last_element = elements[-1]
        
        self._debug_print(f" Dernier élément '{tag}' trouvé (parmi {len(elements)} éléments)")
        
        return last_element