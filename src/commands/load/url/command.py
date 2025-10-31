"""
Commande LOAD URL pour charger le contenu d'une URL
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

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
        Exécute LOAD URL "url" ou LOAD URL variable_name "url"
        
        Args:
            args: [url] ou [variable_name, url] - L'URL à charger avec optionnellement un nom de variable
            variables: Variables disponibles
            
        Returns:
            BeautifulSoup object contenant le HTML parsé
        """
        if len(args) < 1 or len(args) > 2:
            raise ValueError("LOAD URL: Utilisez LOAD URL \"url\" ou LOAD URL variable_name \"url\"")
        
        # Détermine si on a une variable ou juste l'URL
        if len(args) == 1:
            # Format: LOAD URL "url"
            url = self._clean_quotes(args[0])
            variable_name = None
        else:
            # Format: LOAD URL variable_name "url"
            variable_name = args[0]  # Le nom de variable ne doit pas être nettoyé
            url = self._clean_quotes(args[1])
        
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