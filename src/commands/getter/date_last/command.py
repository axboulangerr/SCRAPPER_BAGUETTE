"""
Commande GET DATE LAST pour trouver le dernier élément d'un type donné contenant une date
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import re
import dateutil.parser

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterDateLastCommand(BaseCommand):
    """Commande pour trouver le dernier élément d'un type donné contenant une date"""
    
    def __init__(self):
        self.debug_mode = False
        # Patterns de dates courantes
        self.date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # DD/MM/YYYY ou MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD
            r'\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}',  # DD mois YYYY (français)
            r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},?\s+\d{4}',  # mois DD, YYYY
            r'\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',  # DD mois YYYY (anglais)
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',  # mois DD, YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD (ISO)
            r'\d{2}:\d{2}:\d{2}',  # HH:MM:SS (time)
        ]
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET DATE LAST", "GET DATE")
            print(f"{colored_prefix} {message}")
    
    def _contains_date(self, text: str) -> bool:
        """Vérifie si un texte contient une date"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Vérifie chaque pattern de date
        for pattern in self.date_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        # Essaie aussi le parsing avec dateutil (plus flexible)
        try:
            words = text_lower.split()
            for i in range(len(words)):
                for j in range(i+1, min(i+5, len(words)+1)):
                    candidate = " ".join(words[i:j])
                    if len(candidate) < 50:
                        try:
                            dateutil.parser.parse(candidate, fuzzy=False)
                            return True
                        except:
                            continue
        except:
            pass
        
        return False
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Optional[Tag]:
        """
        Exécute GET DATE LAST "tag"
        
        Args:
            args: [tag] - Le type d'élément à chercher
            variables: Variables disponibles
            
        Returns:
            Tag contenant le dernier élément avec une date trouvé
        """
        self.validate_args(args, 1, "GET DATE LAST")
        
        tag = args[0]
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET DATE LAST: Aucun contenu HTML disponible")
        
        self._debug_print(f"Recherche du dernier élément '{tag}' contenant une date")
        
        # Trouve tous les éléments du type spécifié
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"GET DATE LAST: Aucun élément '{tag}' trouvé")
        
        # Cherche le dernier élément contenant une date (parcours inverse)
        for element in reversed(elements):
            element_text = element.get_text(strip=True)
            if self._contains_date(element_text):
                self._debug_print(f"Dernier élément '{tag}' avec date trouvé (parmi {len(elements)} éléments): {element_text[:100]}...")
                return element
        
        raise ValueError(f"GET DATE LAST: Aucun élément '{tag}' contenant une date trouvé")