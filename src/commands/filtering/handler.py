"""
Handler principal pour les commandes FILTER
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class FilteringHandler(BaseCommand):
    """Handler principal pour toutes les variantes de la commande FILTER"""
    
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
            colored_prefix = CommandColors.colorize_prefix("FILTER", "FILTER")
            print(f"{colored_prefix} {message}")
    
    def _load_subcommands(self):
        """Charge dynamiquement toutes les sous-commandes FILTER disponibles"""
        filtering_dir = Path(__file__).parent
        
        # Parcourt tous les sous-dossiers de filtering/
        for subcommand_dir in filtering_dir.iterdir():
            if subcommand_dir.is_dir() and subcommand_dir.name != "__pycache__":
                command_file = subcommand_dir / "command.py"
                if command_file.exists():
                    self._load_subcommand_module(command_file, subcommand_dir.name)
    
    def _load_subcommand_module(self, command_file: Path, subcommand: str):
        """Charge un module de sous-commande spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"filtering_{subcommand}", command_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe de commande (convention: FilteringSubcommandCommand)
            class_suffix = "".join(word.title() for word in subcommand.split("_"))
            class_name = f"Filtering{class_suffix}Command"
            
            if hasattr(module, class_name):
                command_class = getattr(module, class_name)
                command_instance = command_class()
                
                # Convertit le nom en majuscules pour la clé
                command_key = subcommand.upper()
                self.subcommands[command_key] = command_instance
                
                # Propage immédiatement le mode debug si déjà défini
                if hasattr(command_instance, 'set_debug_mode'):
                    command_instance.set_debug_mode(self.debug_mode)
                
                self._debug_print(f"Sous-commande chargée: {command_key}")
            else:
                self._debug_print(f"Attention: Classe {class_name} non trouvée dans {command_file}")
                
        except Exception as e:
            self._debug_print(f"Erreur lors du chargement de la sous-commande {subcommand}: {e}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """
        Exécute la commande FILTER avec dispatch vers la bonne sous-commande
        
        Args:
            args: [subcommand, WHERE, condition, ...] ou [ONCE, index, WHERE, condition, ...]
            variables: Variables disponibles
            
        Returns:
            Le résultat de la sous-commande
        """
        if len(args) < 3:
            raise ValueError("FILTER: Il faut spécifier une sous-commande et une condition (ex: FILTER ALL WHERE class CONTAINS \"active\")")
        
        subcommand = args[0].upper()
        
        # Gestion spéciale pour FILTER ONCE qui a un index
        if subcommand == "ONCE":
            if len(args) < 5 or args[2].upper() != "WHERE":
                raise ValueError("FILTER ONCE: Syntaxe incorrecte. Utilisez: FILTER ONCE index WHERE condition")
            # Pour ONCE, on passe tous les arguments (index + condition)
            condition_args = args[1:]  # [index, WHERE, condition...]
        else:
            # Vérifie que le mot WHERE est présent
            if args[1].upper() != "WHERE":
                raise ValueError("FILTER: Syntaxe incorrecte. Utilisez: FILTER [ALL|FIRST|LAST] WHERE condition ou FILTER ONCE index WHERE condition")
            # Les arguments de condition commencent après WHERE
            condition_args = args[2:]
        
        self._debug_print(f"Recherche de la sous-commande: {subcommand}")
        self._debug_print(f"Arguments: {' '.join(condition_args)}")
        self._debug_print(f"Sous-commandes disponibles: {list(self.subcommands.keys())}")
        
        if subcommand not in self.subcommands:
            available = ", ".join(sorted(self.subcommands.keys()))
            raise ValueError(f"FILTER: Sous-commande '{subcommand}' inconnue. Disponibles: {available}")
        
        # Vérifie qu'il y a un résultat précédent à traiter
        if '_last_result' not in variables:
            raise ValueError("FILTER: Aucun élément sélectionné. Utilisez d'abord une commande SELECT.")
        
        self._debug_print(f"Dispatch vers {subcommand} avec arguments: {condition_args}")
        
        # Délègue à la sous-commande appropriée
        return self.subcommands[subcommand].execute(condition_args, variables)