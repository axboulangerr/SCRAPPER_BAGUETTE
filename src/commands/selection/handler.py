"""
Handler principal pour la commande SELECT
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class SelectionHandler(BaseCommand):
    """Handler principal pour toutes les variantes de la commande SELECT"""
    
    def __init__(self):
        self.subcommands = {}
        self.debug_mode = False
        self._load_subcommands()
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
        # Propage aux sous-commandes si elles supportent le debug
        for subcommand in self.subcommands.values():
            if hasattr(subcommand, 'set_debug_mode'):
                subcommand.set_debug_mode(debug_mode)
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("SELECT", "SELECT")
            print(f"{colored_prefix} {message}")
    
    def _load_subcommands(self):
        """Charge dynamiquement toutes les sous-commandes SELECT disponibles"""
        select_dir = Path(__file__).parent
        
        # Parcourt tous les sous-dossiers de select/
        for subcommand_dir in select_dir.iterdir():
            if subcommand_dir.is_dir() and subcommand_dir.name != "__pycache__":
                command_file = subcommand_dir / "command.py"
                if command_file.exists():
                    self._load_subcommand_module(command_file, subcommand_dir.name)
    
    def _load_subcommand_module(self, command_file: Path, subcommand: str):
        """Charge un module de sous-commande spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"select_{subcommand}", command_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe de commande (convention: SelectSubcommandCommand)
            class_name = f"Select{subcommand.title()}Command"
            if hasattr(module, class_name):
                command_class = getattr(module, class_name)
                command_instance = command_class()
                self.subcommands[subcommand.upper()] = command_instance
                
                # Propage immédiatement le mode debug si déjà défini
                if hasattr(command_instance, 'set_debug_mode'):
                    command_instance.set_debug_mode(self.debug_mode)
                
                self._debug_print(f"Sous-commande chargée: {subcommand.upper()}")
            else:
                self._debug_print(f"Attention: Classe {class_name} non trouvée dans {command_file}")
                
        except Exception as e:
            self._debug_print(f"Erreur lors du chargement de la sous-commande {subcommand}: {e}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """
        Exécute la commande SELECT avec dispatch vers la bonne sous-commande
        
        Args:
            args: [subcommand, ...] - La sous-commande et ses arguments
            variables: Variables disponibles
            
        Returns:
            Le résultat de la sous-commande
        """
        if len(args) < 1:
            raise ValueError("SELECT: Il faut spécifier une sous-commande (ex: SELECT ALL \"div\")")
        
        subcommand = args[0].upper()
        subcommand_args = args[1:]
        
        if subcommand not in self.subcommands:
            available = ", ".join(self.subcommands.keys())
            raise ValueError(f"SELECT: Sous-commande '{subcommand}' inconnue. Disponibles: {available}")
        
        # Cherche le document HTML original dans les variables
        soup = None
        
        # D'abord cherche dans _original_html (si disponible)
        if '_original_html' in variables:
            soup = variables['_original_html']
        # Sinon regarde si _last_result est un BeautifulSoup
        elif '_last_result' in variables and hasattr(variables['_last_result'], 'find'):
            soup = variables['_last_result']
        else:
            raise ValueError("SELECT: Aucun contenu HTML chargé. Utilisez d'abord LOAD URL ou une autre commande de chargement.")
        
        # Sauvegarde temporairement le document original pour les sous-commandes
        variables['_current_soup'] = soup
        
        self._debug_print(f"Dispatch vers {subcommand} avec {len(subcommand_args)} argument(s): {subcommand_args}")
        
        # Délègue à la sous-commande appropriée
        return self.subcommands[subcommand].execute(subcommand_args, variables)