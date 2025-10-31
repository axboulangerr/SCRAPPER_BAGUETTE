"""
Commande LOAD URL pour charger le contenu d'une URL
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import sys
from pathlib import Path

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class LoadUrlCommand(BaseCommand):
    """Commande pour charger le contenu d'une URL web"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("LOAD URL", "LOAD URL")
            print(f"{colored_prefix} {message}")
    
    def _clean_quotes(self, text: str) -> str:
        """Supprime les guillemets d'ouverture et de fermeture si présents"""
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        return text

    def execute(self, args: List[str], variables: Dict[str, Any]) -> BeautifulSoup:
        """
        Exécute LOAD URL "url" ou LOAD URL variable_name "url" ou LOAD URL variable_name url_variable
        
        Args:
            args: [url] ou [variable_name, url] - L'URL à charger avec optionnellement un nom de variable
            variables: Variables disponibles
            
        Returns:
            BeautifulSoup object contenant le HTML parsé
        """
        if len(args) < 1 or len(args) > 2:
            raise ValueError("LOAD URL: Utilisez LOAD URL \"url\" ou LOAD URL variable_name \"url\" ou LOAD URL variable_name url_variable")
        
        # Détermine si on a une variable ou juste l'URL
        if len(args) == 1:
            # Format: LOAD URL "url"
            url_source = args[0]
            variable_name = None
        else:
            # Format: LOAD URL variable_name "url" ou LOAD URL variable_name url_variable
            variable_name = args[0]
            url_source = args[1]
        
        # Résout l'URL (soit depuis une chaîne, soit depuis une variable)
        url = self._resolve_url(url_source, variables)
        
        try:
            self._debug_print(f"Chargement de l'URL: {url}")
            if variable_name:
                self._debug_print(f"Sauvegarde dans la variable: {variable_name}")
            
            # Configuration des headers pour éviter les blocages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Effectue la requête HTTP
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse le HTML avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Si une variable est spécifiée, sauvegarde dans cette variable
            if variable_name:
                variables[variable_name] = soup
                self._debug_print(f"Contenu HTML sauvegardé dans la variable '{variable_name}'")
            else:
                # Comportement original : sauvegarde dans _last_result et _original_html
                variables['_original_html'] = soup
            
            self._debug_print(f" URL chargée avec succès ({len(response.content)} octets)")
            self._debug_print(f"Titre de la page: {soup.title.string if soup.title else 'Aucun titre'}")
            
            return soup
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erreur lors du chargement de l'URL {url}: {e}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du parsing HTML: {e}")
    
    def _resolve_url(self, url_source: str, variables: Dict[str, Any]) -> str:
        """Résout l'URL depuis une chaîne littérale ou une variable"""
        
        # Si c'est entre guillemets, c'est une URL littérale
        if (url_source.startswith('"') and url_source.endswith('"')) or (url_source.startswith("'") and url_source.endswith("'")):
            return self._clean_quotes(url_source)
        
        # Sinon, c'est une variable
        if url_source in variables:
            url_value = variables[url_source]
            
            # Vérifie que la variable contient bien une URL (string)
            if not isinstance(url_value, str):
                raise ValueError(f"LOAD URL: La variable '{url_source}' doit contenir une URL (string), trouvé: {type(url_value).__name__}")
            
            # Nettoie l'URL
            url_value = url_value.strip()
            
            # Ignore les URLs relatives ou invalides
            if not url_value or url_value in ['#', '/', '#main', '#content'] or url_value.startswith('#'):
                raise ValueError(f"LOAD URL: La variable '{url_source}' contient une URL relative ou invalide: '{url_value}'")
            
            # URLs relatives commençant par /
            if url_value.startswith('/') and not url_value.startswith('//'):
                # Essaie de récupérer le domaine de base depuis _current_soup ou une autre variable
                if '_current_soup' in variables:
                    base_url = self._get_base_url_from_soup(variables['_current_soup'])
                    if base_url:
                        url_value = base_url + url_value
                    else:
                        raise ValueError(f"LOAD URL: URL relative '{url_value}' sans domaine de base disponible")
                else:
                    raise ValueError(f"LOAD URL: URL relative '{url_value}' sans contexte de page de base")
            
            # Vérifie que ça ressemble à une URL complète
            if not (url_value.startswith('http://') or url_value.startswith('https://')):
                # Ajoute https:// si pas de protocole et que ça ressemble à un domaine
                if '.' in url_value and ' ' not in url_value and not url_value.startswith('/'):
                    url_value = 'https://' + url_value
                else:
                    raise ValueError(f"LOAD URL: La variable '{url_source}' ne contient pas une URL valide: '{url_value}'")
            
            return url_value
        else:
            # La variable n'existe pas
            available_vars = [name for name in variables.keys() if not name.startswith('_')]
            if available_vars:
                available_str = ", ".join(available_vars)
                raise ValueError(f"LOAD URL: Variable '{url_source}' non trouvée. Variables disponibles: {available_str}")
            else:
                raise ValueError(f"LOAD URL: Variable '{url_source}' non trouvée. Aucune variable disponible.")
    
    def _get_base_url_from_soup(self, soup) -> str:
        """Extrait l'URL de base depuis un objet BeautifulSoup"""
        try:
            # Cherche la balise base
            base_tag = soup.find('base')
            if base_tag and base_tag.get('href'):
                return base_tag['href'].rstrip('/')
            
            # Fallback : essaie d'extraire depuis les meta ou liens canoniques
            canonical = soup.find('link', {'rel': 'canonical'})
            if canonical and canonical.get('href'):
                canonical_url = canonical['href']
                if canonical_url.startswith('http'):
                    # Extrait le domaine de base
                    from urllib.parse import urlparse
                    parsed = urlparse(canonical_url)
                    return f"{parsed.scheme}://{parsed.netloc}"
            
            return None
        except:
            return None