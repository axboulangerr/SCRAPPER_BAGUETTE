"""
Commande EXTRACT EMAILS pour extraire toutes les adresses email présentes dans le texte des éléments HTML
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

class ExtractionEmailsCommand(BaseCommand):
    """Commande pour extraire toutes les adresses email présentes dans le texte des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT EMAILS", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Extrait toutes les adresses email d'un texte"""
        if not text:
            return []
        
        # Pattern pour capturer les adresses email
        # Supporte la plupart des formats d'email valides
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Supprime les doublons tout en gardant l'ordre
        unique_emails = []
        seen = set()
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        return unique_emails
    
    def _extract_emails_from_attributes(self, element: Tag) -> List[str]:
        """Extrait les emails des attributs href (mailto:) et autres attributs"""
        emails = []
        
        # Cherche dans les liens mailto
        for link in element.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href[7:]  # Supprime "mailto:"
                # Nettoie l'email (supprime les paramètres comme ?subject=...)
                if '?' in email:
                    email = email.split('?')[0]
                if email and '@' in email:
                    emails.append(email)
        
        # Cherche dans tous les attributs qui pourraient contenir des emails
        for attr_name in ['data-email', 'data-mail', 'email', 'mail']:
            if element.has_attr(attr_name):
                attr_value = element[attr_name]
                if isinstance(attr_value, str) and '@' in attr_value:
                    extracted = self._extract_emails_from_text(attr_value)
                    emails.extend(extracted)
        
        return emails
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Exécute EXTRACT EMAILS
        
        Args:
            args: Arguments supplémentaires (généralement vide)
            variables: Variables disponibles
            
        Returns:
            List[str] contenant toutes les adresses email trouvées
        """
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT EMAILS: Aucun élément à traiter")
        
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
            raise ValueError("EXTRACT EMAILS: Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction des emails de {len(elements_to_process)} élément(s)")
        
        # Extrait tous les emails de tous les éléments
        all_emails = []
        for element in elements_to_process:
            # Extrait depuis le texte
            text = element.get_text()
            text_emails = self._extract_emails_from_text(text)
            all_emails.extend(text_emails)
            
            # Extrait depuis les attributs
            attr_emails = self._extract_emails_from_attributes(element)
            all_emails.extend(attr_emails)
        
        # Supprime les doublons finaux
        unique_emails = []
        seen = set()
        for email in all_emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        self._debug_print(f"{len(unique_emails)} email(s) unique(s) trouvé(s)")
        
        # Si debug activé, affiche un aperçu des emails trouvés
        if self.debug_mode and unique_emails:
            preview_count = min(5, len(unique_emails))
            self._debug_print(f"  Emails trouvés (premiers {preview_count}): {', '.join(unique_emails[:preview_count])}")
            if len(unique_emails) > 5:
                self._debug_print(f"  ... et {len(unique_emails) - 5} autre(s)")
        
        return unique_emails