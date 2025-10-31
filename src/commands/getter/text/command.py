"""
Commande GET TEXT pour extraire le texte des éléments HTML
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterTextCommand(BaseCommand):
    """Commande pour extraire le texte des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET TEXT", "GET")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Exécute GET TEXT
        
        Args:
            args: [] - Aucun argument requis
            variables: Variables disponibles
            
        Returns:
            List[str] contenant le texte extrait de tous les éléments
        """
        if len(args) != 0:
            raise ValueError("GET TEXT: Aucun argument requis")
        
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("GET TEXT: Aucun élément à traiter")
        
        texts = []
        
        if isinstance(last_result, ResultSet):
            self._debug_print(f"Extraction de texte de {len(last_result)} élément(s)")
            for element in last_result:
                if hasattr(element, 'get_text'):
                    text = element.get_text(strip=True)
                    if text:  # Ignore les textes vides
                        texts.append(text)
        elif isinstance(last_result, Tag):
            self._debug_print("Extraction de texte d'un élément unique")
            text = last_result.get_text(strip=True)
            if text:
                texts.append(text)
        elif isinstance(last_result, BeautifulSoup):
            self._debug_print("Extraction de texte de la page complète")
            text = last_result.get_text(strip=True)
            if text:
                texts.append(text)
        else:
            raise ValueError(f"GET TEXT: Type de données non supporté: {type(last_result).__name__}")
        
        self._debug_print(f"{len(texts)} texte(s) extrait(s)")
        
        return texts