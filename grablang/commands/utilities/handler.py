"""
Handler principal pour la commande UTILITIES
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class UtilitiesHandler(BaseCommand):
    """Handler principal pour toutes les commandes utilities"""
    
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
            colored_prefix = CommandColors.colorize_prefix("UTILITIES", "SAVE")
            print(f"{colored_prefix} {message}")
    
    def _load_subcommands(self):
        """Charge dynamiquement toutes les sous-commandes utilities disponibles"""
        utilities_dir = Path(__file__).parent
        
        # Parcourt tous les sous-dossiers de utilities/
        for subcommand_dir in utilities_dir.iterdir():
            if subcommand_dir.is_dir() and subcommand_dir.name != "__pycache__":
                command_file = subcommand_dir / "command.py"
                if command_file.exists():
                    self._load_subcommand_module(command_file, subcommand_dir.name)
    
    def _load_subcommand_module(self, command_file: Path, subcommand: str):
        """Charge un module de sous-commande spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"utilities_{subcommand}", command_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe de commande (convention: UtilitiesSubcommandCommand)
            class_name = f"Utilities{subcommand.title()}Command"
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
        Exécute une commande utilities avec dispatch vers la bonne sous-commande
        
        Args:
            args: [subcommand, ...] - La sous-commande et ses arguments
            variables: Variables disponibles
            
        Returns:
            Le résultat de la sous-commande
        """
        if len(args) < 1:
            raise ValueError("UTILITIES: Il faut spécifier une sous-commande")
        
        subcommand = args[0].upper()
        subcommand_args = args[1:]
        
        if subcommand not in self.subcommands:
            available = ", ".join(self.subcommands.keys())
            raise ValueError(f"UTILITIES: Sous-commande '{subcommand}' inconnue. Disponibles: {available}")
        
        self._debug_print(f"Dispatch vers {subcommand} avec {len(subcommand_args)} argument(s): {subcommand_args}")
        
        # Délègue à la sous-commande appropriée
        return self.subcommands[subcommand].execute(subcommand_args, variables)