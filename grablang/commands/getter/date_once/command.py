"""
Commande GET DATE ONCE pour trouver un élément spécifique par index contenant une date
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

class GetterDateOnceCommand(BaseCommand):
    """Commande pour trouver un élément spécifique par index contenant une date"""
    
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
            colored_prefix = CommandColors.colorize_prefix("GET DATE ONCE", "GET DATE")
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
        Exécute GET DATE ONCE "tag" index
        
        Args:
            args: [tag, index] - Le type d'élément et l'index (1-based) à vérifier
            variables: Variables disponibles
            
        Returns:
            Tag contenant l'élément à l'index spécifié s'il contient une date
        """
        self.validate_args(args, 2, "GET DATE ONCE")
        
        tag = args[0]
        try:
            index = int(args[1])
        except ValueError:
            raise ValueError(f"GET DATE ONCE: L'index doit être un nombre entier, reçu '{args[1]}'")
        
        if index < 1:
            raise ValueError(f"GET DATE ONCE: L'index doit être supérieur à 0, reçu {index}")
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET DATE ONCE: Aucun contenu HTML disponible")
        
        self._debug_print(f"Vérification de l'élément '{tag}' à l'index {index} pour une date")
        
        # Trouve tous les éléments du type spécifié
        elements = soup.find_all(tag)
        
        if not elements:
            raise ValueError(f"GET DATE ONCE: Aucun élément '{tag}' trouvé")
        
        # Vérifie que l'index existe (conversion 1-based vers 0-based)
        if index > len(elements):
            raise ValueError(f"GET DATE ONCE: Index {index} trop élevé. Il y a seulement {len(elements)} élément(s) '{tag}'")
        
        selected_element = elements[index - 1]  # Conversion 1-based vers 0-based
        element_text = selected_element.get_text(strip=True)
        
        if self._contains_date(element_text):
            self._debug_print(f"Élément '{tag}' à l'index {index} contient une date: {element_text[:100]}...")
            return selected_element
        else:
            raise ValueError(f"GET DATE ONCE: L'élément '{tag}' à l'index {index} ne contient pas de date")