"""
Commande EXTRACT URLS pour extraire toutes les URLs présentes dans le texte et les attributs des éléments HTML
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

class ExtractionUrlsCommand(BaseCommand):
    """Commande pour extraire toutes les URLs présentes dans le texte et les attributs des éléments HTML"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT URLS", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extrait toutes les URLs d'un texte"""
        if not text:
            return []
        
        # Pattern pour capturer les URLs dans le texte
        # Supporte http://, https://, ftp://, et www.
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|ftp://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+\.[a-zA-Z]{2,}'
        urls = re.findall(url_pattern, text)
        
        # Nettoie les URLs (supprime la ponctuation de fin)
        cleaned_urls = []
        for url in urls:
            # Supprime la ponctuation de fin courante
            url = re.sub(r'[.,;:!?)\]}]+$', '', url)
            if url:
                cleaned_urls.append(url)
        
        return cleaned_urls
    
    def _extract_urls_from_attributes(self, element: Tag) -> List[str]:
        """Extrait les URLs des attributs HTML (href, src, action, etc.)"""
        urls = []
        
        # Attributs couramment utilisés pour les URLs
        url_attributes = ['href', 'src', 'action', 'data-url', 'data-link', 'data-href', 'cite', 'formaction']
        
        # Cherche dans l'élément lui-même
        for attr in url_attributes:
            if element.has_attr(attr):
                url = element[attr]
                if isinstance(url, str) and url.strip():
                    # Filtre les URLs valides (ignore javascript:, mailto:, #, etc.)
                    if self._is_valid_url(url):
                        urls.append(url.strip())
        
        # Cherche dans tous les sous-éléments
        for sub_element in element.find_all(True):
            for attr in url_attributes:
                if sub_element.has_attr(attr):
                    url = sub_element[attr]
                    if isinstance(url, str) and url.strip():
                        if self._is_valid_url(url):
                            urls.append(url.strip())
        
        return urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Vérifie si une URL est valide (pas javascript:, mailto:, etc.)"""
        url = url.lower().strip()
        
        # Ignore les URLs non-web
        invalid_schemes = ['javascript:', 'mailto:', 'tel:', 'sms:', 'data:']
        for scheme in invalid_schemes:
            if url.startswith(scheme):
                return False
        
        # Ignore les ancres simples
        if url.startswith('#'):
            return False
        
        # Accepte les URLs qui commencent par http/https/ftp/www ou sont relatives
        valid_patterns = [
            r'^https?://',
            r'^ftp://',
            r'^www\.',
            r'^/',  # URLs relatives absolues
            r'^[a-zA-Z0-9]',  # URLs relatives
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Exécute EXTRACT URLS
        
        Args:
            args: Arguments supplémentaires (généralement vide)
            variables: Variables disponibles
            
        Returns:
            List[str] contenant toutes les URLs trouvées
        """
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT URLS: Aucun élément à traiter")
        
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
            raise ValueError("EXTRACT URLS: Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction des URLs de {len(elements_to_process)} élément(s)")
        
        # Extrait toutes les URLs de tous les éléments
        all_urls = []
        for element in elements_to_process:
            # Extrait depuis le texte
            text = element.get_text()
            text_urls = self._extract_urls_from_text(text)
            all_urls.extend(text_urls)
            
            # Extrait depuis les attributs
            attr_urls = self._extract_urls_from_attributes(element)
            all_urls.extend(attr_urls)
        
        # Supprime les doublons finaux
        unique_urls = []
        seen = set()
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        self._debug_print(f"{len(unique_urls)} URL(s) unique(s) trouvée(s)")
        
        # Si debug activé, affiche un aperçu des URLs trouvées
        if self.debug_mode and unique_urls:
            preview_count = min(5, len(unique_urls))
            self._debug_print(f"  URLs trouvées (premières {preview_count}):")
            for i, url in enumerate(unique_urls[:preview_count]):
                preview_url = url[:80] + "..." if len(url) > 80 else url
                self._debug_print(f"    {i+1}. {preview_url}")
            if len(unique_urls) > 5:
                self._debug_print(f"  ... et {len(unique_urls) - 5} autre(s)")
        
        return unique_urls