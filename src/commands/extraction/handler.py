"""
Handler principal pour la commande EXTRACT
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Union
from bs4 import BeautifulSoup, Tag, ResultSet
import importlib.util
import os

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class ExtractionHandler(BaseCommand):
    """Handler principal pour la commande EXTRACT"""
    
    def __init__(self):
        self.debug_mode = False
        self.subcommands = {}
        self._load_subcommands()
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
        # Propage le mode debug aux sous-commandes
        for subcommand in self.subcommands.values():
            if hasattr(subcommand, 'set_debug_mode'):
                subcommand.set_debug_mode(debug_mode)
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _load_subcommands(self):
        """Charge dynamiquement toutes les sous-commandes depuis les sous-dossiers"""
        extraction_dir = Path(__file__).parent
        
        # Liste des sous-commandes attendues
        expected_subcommands = [
            'text', 'text_clean', 'numbers', 'emails', 'urls', 'regex'
        ]
        
        for subcommand_name in expected_subcommands:
            subcommand_dir = extraction_dir / subcommand_name
            command_file = subcommand_dir / "command.py"
            
            if command_file.exists():
                try:
                    # Charge le module dynamiquement
                    spec = importlib.util.spec_from_file_location(
                        f"extraction_{subcommand_name}", 
                        command_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Cherche la classe de commande (par convention : ExtractionXxxCommand)
                    class_name = f"Extraction{subcommand_name.replace('_', '').title()}Command"
                    if hasattr(module, class_name):
                        self.subcommands[subcommand_name] = getattr(module, class_name)()
                        self._debug_print(f"Sous-commande '{subcommand_name}' chargée")
                    else:
                        self._debug_print(f"Classe '{class_name}' non trouvée dans {command_file}")
                        
                except Exception as e:
                    self._debug_print(f"Erreur lors du chargement de '{subcommand_name}': {e}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Union[str, List[str]]:
        """
        Exécute la commande EXTRACT
        
        Args:
            args: Arguments de la commande (ex: ["TEXT"], ["TEXT", "CLEAN"], ["NUMBERS"])
            variables: Variables disponibles
            
        Returns:
            String ou liste de strings selon la sous-commande
        """
        if len(args) < 1:
            raise ValueError("EXTRACT: Spécifiez le type d'extraction. Exemples: TEXT, TEXT CLEAN, NUMBERS, EMAILS, URLS")
        
        # Détermine la sous-commande
        subcommand_key = None
        remaining_args = []
        
        if len(args) >= 2 and args[0].upper() == "TEXT" and args[1].upper() == "CLEAN":
            subcommand_key = "text_clean"
            remaining_args = args[2:]
        elif args[0].upper() == "TEXT":
            subcommand_key = "text"
            remaining_args = args[1:]
        elif args[0].upper() == "NUMBERS":
            subcommand_key = "numbers"
            remaining_args = args[1:]
        elif args[0].upper() == "EMAILS":
            subcommand_key = "emails"
            remaining_args = args[1:]
        elif args[0].upper() == "URLS":
            subcommand_key = "urls"
            remaining_args = args[1:]
        elif args[0].upper() == "REGEX":
            subcommand_key = "regex"
            remaining_args = args[1:]
        else:
            available_commands = list(self.subcommands.keys())
            raise ValueError(f"EXTRACT: Type d'extraction non reconnu '{args[0]}'. Disponibles: TEXT, TEXT CLEAN, NUMBERS, EMAILS, URLS, REGEX")
        
        # Vérifie que la sous-commande existe
        if subcommand_key not in self.subcommands:
            raise ValueError(f"EXTRACT: Sous-commande '{subcommand_key}' non implémentée")
        
        self._debug_print(f"Exécution de EXTRACT {subcommand_key.upper()} avec arguments: {remaining_args}")
        
        # Exécute la sous-commande
        subcommand = self.subcommands[subcommand_key]
        result = subcommand.execute(remaining_args, variables)
        
        # Met à jour _last_result
        variables['_last_result'] = result
        
        return result