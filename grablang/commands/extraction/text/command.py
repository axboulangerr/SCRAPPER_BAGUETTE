"""
Commande EXTRACT TEXT pour extraire le contenu textuel des éléments HTML
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import sys
from pathlib import Path

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class ExtractionTextCommand(BaseCommand):
    """Commande pour extraire le contenu textuel des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT TEXT", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _extract_text_from_element(self, element: Tag) -> str:
        """Extrait le texte d'un élément HTML"""
        return element.get_text(strip=True)
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Union[str, List[str]]:
        """
        Exécute EXTRACT TEXT
        
        Args:
            args: Arguments supplémentaires (généralement vide)
            variables: Variables disponibles
            
        Returns:
            String si un seul élément, List[str] si plusieurs éléments
        """
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT TEXT: Aucun élément à traiter")
        
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
            raise ValueError("EXTRACT TEXT: Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction du texte de {len(elements_to_process)} élément(s)")
        
        # Extrait le texte de chaque élément
        extracted_texts = []
        for element in elements_to_process:
            text = self._extract_text_from_element(element)
            if text:  # Ne garde que les textes non vides
                extracted_texts.append(text)
        
        self._debug_print(f"{len(extracted_texts)} texte(s) extrait(s)")
        
        # Si debug activé, affiche un aperçu
        if self.debug_mode and extracted_texts:
            for i, text in enumerate(extracted_texts[:3]):  # Affiche les 3 premiers
                preview = text[:100] + "..." if len(text) > 100 else text
                self._debug_print(f"  Texte {i+1}: '{preview}'")
            if len(extracted_texts) > 3:
                self._debug_print(f"  ... et {len(extracted_texts) - 3} autre(s)")
        
        # Retourne string si un seul élément, liste sinon
        if len(extracted_texts) == 1:
            return extracted_texts[0]
        elif len(extracted_texts) == 0:
            raise ValueError("EXTRACT TEXT: Aucun texte trouvé dans les éléments")
        else:
            return extracted_texts