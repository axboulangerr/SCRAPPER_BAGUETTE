"""
Handler principal pour la commande GET
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterHandler(BaseCommand):
    """Handler principal pour toutes les variantes de la commande GET"""
    
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
            colored_prefix = CommandColors.colorize_prefix("GET", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _load_subcommands(self):
        """Charge dynamiquement toutes les sous-commandes GET disponibles"""
        getter_dir = Path(__file__).parent
        
        # Parcourt tous les sous-dossiers de getter/
        for subcommand_dir in getter_dir.iterdir():
            if subcommand_dir.is_dir() and subcommand_dir.name != "__pycache__":
                command_file = subcommand_dir / "command.py"
                if command_file.exists():
                    self._load_subcommand_module(command_file, subcommand_dir.name)
    
    def _load_subcommand_module(self, command_file: Path, subcommand: str):
        """Charge un module de sous-commande spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"getter_{subcommand}", command_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe de commande (convention: GetterSubcommandCommand)
            # Gère les noms avec underscores (ex: attr_first -> AttrFirst)
            class_suffix = "".join(word.title() for word in subcommand.split("_"))
            class_name = f"Getter{class_suffix}Command"
            
            if hasattr(module, class_name):
                command_class = getattr(module, class_name)
                command_instance = command_class()
                
                # Convertit le nom en majuscules avec underscores pour la clé
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
        Exécute la commande GET avec dispatch vers la bonne sous-commande
        
        Args:
            args: [subcommand, ...] - La sous-commande et ses arguments
            variables: Variables disponibles
            
        Returns:
            Le résultat de la sous-commande
        """
        if len(args) < 1:
            raise ValueError("GET: Il faut spécifier une sous-commande (ex: GET ATTR \"href\")")
        
        # Pour les commandes composées comme ATTR_FIRST, l'argument vient déjà formaté
        subcommand = args[0].upper()
        subcommand_args = args[1:]
        
        self._debug_print(f"Recherche de la sous-commande: {subcommand}")
        self._debug_print(f"Sous-commandes disponibles: {list(self.subcommands.keys())}")
        
        if subcommand not in self.subcommands:
            available = ", ".join(sorted(self.subcommands.keys()))
            raise ValueError(f"GET: Sous-commande '{subcommand}' inconnue. Disponibles: {available}")
        
        # Vérifie qu'il y a un résultat précédent à traiter pour les commandes qui en ont besoin
        if subcommand in ['ATTR'] and '_last_result' not in variables:
            raise ValueError("GET: Aucun élément sélectionné. Utilisez d'abord une commande SELECT.")
        
        self._debug_print(f"Dispatch vers {subcommand} avec {len(subcommand_args)} argument(s): {subcommand_args}")
        
        # Délègue à la sous-commande appropriée
        return self.subcommands[subcommand].execute(subcommand_args, variables)