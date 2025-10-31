"""
Commande EXTRACT NUMBERS pour extraire tous les nombres présents dans le texte des éléments HTML
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import sys
from pathlib import Path
import re

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class ExtractionNumbersCommand(BaseCommand):
    """Commande pour extraire tous les nombres présents dans le texte des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT NUMBERS", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _extract_numbers_from_text(self, text: str) -> List[str]:
        """Extrait tous les nombres d'un texte"""
        if not text:
            return []
        
        # Pattern pour capturer les nombres (entiers et décimaux)
        # Supporte: 123, 123.45, -123, -123.45, 1,234.56, etc.
        number_pattern = r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?'
        numbers = re.findall(number_pattern, text)
        
        # Nettoie et valide les nombres trouvés
        cleaned_numbers = []
        for num in numbers:
            # Supprime les virgules de séparation des milliers
            cleaned_num = num.replace(',', '')
            try:
                # Vérifie que c'est bien un nombre valide
                float(cleaned_num)
                cleaned_numbers.append(cleaned_num)
            except ValueError:
                # Ignore les faux positifs
                continue
        
        return cleaned_numbers
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Exécute EXTRACT NUMBERS
        
        Args:
            args: Arguments supplémentaires (généralement vide)
            variables: Variables disponibles
            
        Returns:
            List[str] contenant tous les nombres trouvés
        """
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT NUMBERS: Aucun élément à traiter")
        
        elements_to_process = []
        if isinstance(last_result, ResultSet):
            elements_to_process = list(last_result)
        elif isinstance(last_result, Tag):
            elements_to_process = [last_result]
        elif isinstance(last_result, BeautifulSoup):
            # Si c'est une page complète, on prend le body ou html
            body = last_result.body if last_result.body else last_result
            elements_to_process = [body]
        else:
            raise ValueError("EXTRACT NUMBERS: Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction des nombres de {len(elements_to_process)} élément(s)")
        
        # Extrait tous les nombres de tous les éléments
        all_numbers = []
        for element in elements_to_process:
            text = element.get_text()
            numbers = self._extract_numbers_from_text(text)
            all_numbers.extend(numbers)
        
        self._debug_print(f"{len(all_numbers)} nombre(s) trouvé(s)")
        
        # Si debug activé, affiche un aperçu des nombres trouvés
        if self.debug_mode and all_numbers:
            preview_count = min(10, len(all_numbers))
            self._debug_print(f"  Nombres trouvés (premiers {preview_count}): {', '.join(all_numbers[:preview_count])}")
            if len(all_numbers) > 10:
                self._debug_print(f"  ... et {len(all_numbers) - 10} autre(s)")
        
        return all_numbers