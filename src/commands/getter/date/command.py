"""
Commande GET DATE pour trouver les éléments contenant des dates
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any
import sys
from pathlib import Path
import re
from datetime import datetime
import dateutil.parser

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterDateCommand(BaseCommand):
    """Commande pour trouver les éléments contenant des dates"""
    
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
            colored_prefix = CommandColors.colorize_prefix("GET DATE", "EXTRACT")
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
            # Ne teste que les chaînes courtes pour éviter de parser tout le contenu
            words = text_lower.split()
            for i in range(len(words)):
                # Teste des combinaisons de 1-4 mots
                for j in range(i+1, min(i+5, len(words)+1)):
                    candidate = " ".join(words[i:j])
                    if len(candidate) < 50:  # Limite la longueur pour éviter les faux positifs
                        try:
                            dateutil.parser.parse(candidate, fuzzy=False)
                            return True
                        except:
                            continue
        except:
            pass
        
        return False
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[Tag]:
        """
        Exécute GET DATE "tag" (optionnel)
        
        Args:
            args: [tag] (optionnel) - Le type d'élément à chercher, sinon cherche dans tout le document
            variables: Variables disponibles
            
        Returns:
            List[Tag] contenant les éléments avec des dates
        """
        # Tag est optionnel
        if len(args) > 1:
            raise ValueError("GET DATE: Trop d'arguments. Usage: GET DATE [\"tag\"]")
        
        tag_filter = args[0] if args else None
        
        # Utilise le document HTML original si disponible
        if '_original_html' in variables:
            soup = variables['_original_html']
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("GET DATE: Aucun contenu HTML disponible")
        
        self._debug_print(f"Recherche d'éléments avec des dates{f' dans les balises {tag_filter}' if tag_filter else ''}")
        
        # Trouve tous les éléments ou seulement ceux du type spécifié
        if tag_filter:
            elements = soup.find_all(tag_filter)
        else:
            # Cherche dans tous les éléments qui ont du texte
            elements = soup.find_all(text=True)
            # Récupère les éléments parents de ces textes
            parent_elements = []
            for text in elements:
                if text.parent and hasattr(text.parent, 'name'):
                    parent_elements.append(text.parent)
            elements = list(set(parent_elements))  # Supprime les doublons
        
        date_elements = []
        
        for element in elements:
            if isinstance(element, Tag):
                # Récupère le texte de l'élément
                element_text = element.get_text(strip=True)
                
                if self._contains_date(element_text):
                    date_elements.append(element)
                    self._debug_print(f"Date trouvée dans <{element.name}>: {element_text[:100]}...")
        
        self._debug_print(f"{len(date_elements)} élément(s) avec des dates trouvé(s)")
        
        return date_elements