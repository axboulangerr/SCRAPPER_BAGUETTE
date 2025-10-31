"""
Commande EXTRACT TEXT CLEAN pour extraire le contenu textuel nettoyé des éléments HTML
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

class ExtractionTextcleanCommand(BaseCommand):
    """Commande pour extraire le contenu textuel nettoyé des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT TEXT CLEAN", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte en supprimant les espaces multiples, tabulations, etc."""
        if not text:
            return ""
        
        # Supprime les caractères de contrôle et normalise les espaces
        text = re.sub(r'\s+', ' ', text)  # Remplace tous les espaces multiples par un seul
        text = re.sub(r'[\t\n\r\f\v]', ' ', text)  # Remplace les caractères de saut par des espaces
        text = text.strip()  # Supprime les espaces en début et fin
        
        return text
    
    def _extract_clean_text_from_element(self, element: Tag) -> str:
        """Extrait et nettoie le texte d'un élément HTML"""
        raw_text = element.get_text()
        return self._clean_text(raw_text)
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Union[str, List[str]]:
        """
        Exécute EXTRACT TEXT CLEAN
        
        Args:
            args: Arguments supplémentaires (généralement vide)
            variables: Variables disponibles
            
        Returns:
            String si un seul élément, List[str] si plusieurs éléments
        """
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT TEXT CLEAN: Aucun élément à traiter")
        
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
            raise ValueError("EXTRACT TEXT CLEAN: Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction et nettoyage du texte de {len(elements_to_process)} élément(s)")
        
        # Extrait et nettoie le texte de chaque élément
        extracted_texts = []
        for element in elements_to_process:
            clean_text = self._extract_clean_text_from_element(element)
            if clean_text:  # Ne garde que les textes non vides après nettoyage
                extracted_texts.append(clean_text)
        
        self._debug_print(f"{len(extracted_texts)} texte(s) nettoyé(s) extrait(s)")
        
        # Si debug activé, affiche un aperçu
        if self.debug_mode and extracted_texts:
            for i, text in enumerate(extracted_texts[:3]):  # Affiche les 3 premiers
                preview = text[:100] + "..." if len(text) > 100 else text
                self._debug_print(f"  Texte nettoyé {i+1}: '{preview}'")
            if len(extracted_texts) > 3:
                self._debug_print(f"  ... et {len(extracted_texts) - 3} autre(s)")
        
        # Retourne string si un seul élément, liste sinon
        if len(extracted_texts) == 1:
            return extracted_texts[0]
        elif len(extracted_texts) == 0:
            raise ValueError("EXTRACT TEXT CLEAN: Aucun texte trouvé dans les éléments")
        else:
            return extracted_texts