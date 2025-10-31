"""
Commande SELECT ALL pour récupérer tous les éléments correspondant à un sélecteur
"""
from bs4 import BeautifulSoup, ResultSet
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class SelectAllCommand(BaseCommand):
    """Commande pour sélectionner tous les éléments correspondant à un tag"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("SELECT ALL", "SELECT ALL")
            print(f"{colored_prefix} {message}")
    
    def _clean_quotes(self, text: str) -> str:
        """Supprime les guillemets d'ouverture et de fermeture si présents"""
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        return text

    def execute(self, args: List[str], variables: Dict[str, Any]) -> ResultSet:
        """
        Exécute SELECT ALL "tag"
        
        Args:
            args: [tag] - Le tag HTML à rechercher
            variables: Variables disponibles
            
        Returns:
            ResultSet contenant tous les éléments trouvés
        """
        self.validate_args(args, 1, "SELECT ALL")
        
        tag = self._clean_quotes(args[0])  # Nettoie les guillemets
        soup = variables['_current_soup']
        
        if not isinstance(soup, BeautifulSoup):
            raise ValueError("SELECT ALL: Le contenu chargé n'est pas un document HTML valide")
        
        self._debug_print(f"Recherche de tous les éléments '{tag}'")
        
        # Utilise find_all pour récupérer tous les éléments
        elements = soup.find_all(tag)
        
        self._debug_print(f" {len(elements)} élément(s) '{tag}' trouvé(s)")
        
        return elements