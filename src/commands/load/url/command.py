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
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> BeautifulSoup:
        """
        Exécute LOAD URL "url"
        
        Args:
            args: [url] - L'URL à charger
            variables: Variables disponibles
            
        Returns:
            BeautifulSoup object contenant le HTML parsé
        """
        self.validate_args(args, 1, "LOAD URL")
        
        url = args[0]
        
        try:
            self._debug_print(f"Chargement de l'URL: {url}")
            
            # Configuration des headers pour éviter les blocages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Effectue la requête HTTP
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse le HTML avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Sauvegarde le document original pour les commandes SELECT
            variables['_original_html'] = soup
            
            self._debug_print(f" URL chargée avec succès ({len(response.content)} octets)")
            self._debug_print(f"Titre de la page: {soup.title.string if soup.title else 'Aucun titre'}")
            
            return soup
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erreur lors du chargement de l'URL {url}: {e}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du parsing HTML: {e}")