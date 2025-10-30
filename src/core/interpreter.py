"""
Interpréteur principal pour les fichiers .grab
"""
import re
import argparse
from typing import Dict, Any, List
from pathlib import Path
import importlib.util
from colors import CommandColors

class GrabInterpreter:
    def __init__(self, debug_mode: bool = False):
        self.variables = {}
        self.commands = {}
        self.debug_mode = debug_mode
        self._load_commands()
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("DEBUG", "DEBUG")
            print(f"{colored_prefix} {message}")
    
    def _load_commands(self):
        """Charge dynamiquement toutes les commandes disponibles"""
        commands_dir = Path(__file__).parent.parent / "commands"
        
        # Parcourt tous les dossiers de commandes
        for category_dir in commands_dir.iterdir():
            if category_dir.is_dir():
                # Vérifie d'abord s'il y a un handler dans ce dossier
                handler_file = category_dir / "handler.py"
                if handler_file.exists():
                    self._load_handler_module(handler_file, category_dir.name)
                else:
                    # Sinon, charge les commandes individuelles
                    for command_dir in category_dir.iterdir():
                        if command_dir.is_dir():
                            # Cherche un fichier command.py dans chaque sous-dossier
                            command_file = command_dir / "command.py"
                            if command_file.exists():
                                self._load_command_module(command_file, category_dir.name, command_dir.name)
    
    def _load_handler_module(self, handler_file: Path, category: str):
        """Charge un module handler spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"{category}_handler", handler_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe handler (convention: CategoryHandler)
            class_name = f"{category.title()}Handler"
            if hasattr(module, class_name):
                handler_class = getattr(module, class_name)
                handler_instance = handler_class()
                command_key = category.upper()
                self.commands[command_key] = handler_instance
                
                # Propage le mode debug au handler
                if hasattr(handler_instance, 'set_debug_mode'):
                    handler_instance.set_debug_mode(self.debug_mode)
                
                self._debug_print(f"Handler chargé: {command_key}")
                
                # Ajoute des alias pour certains handlers
                if command_key == "SELECTION":
                    self.commands["SELECT"] = handler_instance
                    self._debug_print(f"Alias ajouté: SELECT -> {command_key}")
                elif command_key == "UTILITIES":
                    self.commands["SAVE"] = handler_instance
                    self.commands["USE"] = handler_instance
                    self._debug_print(f"Alias ajouté: SAVE -> {command_key}")
                    self._debug_print(f"Alias ajouté: USE -> {command_key}")
                elif command_key == "GETTER":
                    self.commands["GET"] = handler_instance
                    self._debug_print(f"Alias ajouté: GET -> {command_key}")
                
            else:
                self._debug_print(f"Attention: Classe {class_name} non trouvée dans {handler_file}")
                
        except Exception as e:
            self._debug_print(f"Erreur lors du chargement du handler {category}: {e}")
    
    def _load_command_module(self, command_file: Path, category: str, command: str):
        """Charge un module de commande spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(f"{category}_{command}", command_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Récupère la classe de commande (convention: CategoryCommandCommand)
            class_name = f"{category.title()}{command.title()}Command"
            if hasattr(module, class_name):
                command_class = getattr(module, class_name)
                command_key = f"{category.upper()}_{command.upper()}"
                self.commands[command_key] = command_class()
                self._debug_print(f"Commande chargée: {command_key}")
                    
        except Exception as e:
            self._debug_print(f"Erreur lors du chargement de la commande {category}/{command}: {e}")
    
    def execute_file(self, file_path: str):
        """Exécute un fichier .grab"""
        self._debug_print(f"Lecture du fichier: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._debug_print(f"Contenu du fichier ({len(content)} caractères):")
        if self.debug_mode:
            for i, line in enumerate(content.split('\n'), 1):
                print(f"  {i:2d}: {line}")
        
        self.execute_script(content)
    
    def execute_script(self, script: str):
        """Exécute un script .grab"""
        lines = script.strip().split('\n')
        self._debug_print(f"Début de l'exécution du script ({len(lines)} lignes)")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ignore les lignes vides et les commentaires
            if not line or line.startswith('#'):
                self._debug_print(f"Ligne {line_num}: ignorée (vide ou commentaire)")
                continue
            
            self._debug_print(f"Ligne {line_num}: {line}")
            
            try:
                self._execute_line(line)
                self._debug_print(f"Ligne {line_num}:  exécutée avec succès")
            except Exception as e:
                print(f"Erreur ligne {line_num}: {e}")
                print(f"   Ligne: {line}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()
        
        self._debug_print("Fin de l'exécution du script")
    
    def _execute_line(self, line: str):
        """Exécute une ligne de commande"""
        # Parse la ligne pour extraire la commande et ses arguments
        tokens = self._parse_line(line)
        self._debug_print(f"Tokens parsés: {tokens}")
        
        if not tokens:
            return
        
        # Gère les commandes composées (COMMAND SUBCOMMAND avec espace)
        command_key = None
        args = []
        
        if len(tokens) >= 2:
            # Essaie la forme COMMAND SUBCOMMAND (avec espace dans le script)
            potential_key = f"{tokens[0].upper()}_{tokens[1].upper()}"
            if potential_key in self.commands:
                command_key = potential_key
                args = tokens[2:]
                self._debug_print(f"Commande composée trouvée: {command_key}")
        
        # Si pas trouvé, essaie la commande simple
        if command_key is None:
            if tokens[0].upper() in self.commands:
                command_key = tokens[0].upper()
                args = tokens[1:]
                self._debug_print(f"Commande simple trouvée: {command_key}")
        
        # Vérifie si la commande existe
        if command_key and command_key in self.commands:
            self._debug_print(f"Exécution de {command_key} avec arguments: {args}")
            
            # Gestion spéciale pour SAVE, USE et GET qui passent par leurs handlers
            if command_key in ["SAVE", "USE"]:
                # Prépend le nom de la sous-commande aux arguments
                args = [command_key] + args
            # GET n'a pas besoin de préfixer car les arguments sont déjà corrects
            
            # Exécute la commande avec les arguments restants
            result = self.commands[command_key].execute(args, self.variables)
            
            # Si la commande retourne un résultat, on peut le stocker
            if result is not None:
                self.variables['_last_result'] = result
                self._debug_print(f"Résultat stocké dans _last_result (type: {type(result).__name__})")
        else:
            self._debug_print(f"Aucune commande trouvée, vérification des commandes spéciales")
            # Vérifie les commandes spéciales (COUNT, etc.)
            self._handle_special_commands(tokens)
    
    def _parse_line(self, line: str) -> List[str]:
        """Parse une ligne en tokens, en gérant les chaînes entre guillemets"""
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(line):
            char = line[i]
            
            if not in_quotes:
                if char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif char.isspace():
                    if current_token:
                        tokens.append(current_token)
                        current_token = ""
                else:
                    current_token += char
            else:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_token += char
            
            i += 1
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _handle_special_commands(self, tokens: List[str]):
        """Gère les commandes spéciales comme SAVE, COUNT, etc."""
        if tokens[0] == "SAVE" and len(tokens) >= 2:
            # SAVE variable_name
            if '_last_result' in self.variables:
                self.variables[tokens[1]] = self.variables['_last_result']
                self._debug_print(f"Variable {tokens[1]} = {type(self.variables[tokens[1]]).__name__}")
        
        elif tokens[0] == "COUNT" and len(tokens) >= 3 and tokens[1] == "FROM":
            # COUNT FROM variable_name
            var_name = tokens[2]
            if var_name in self.variables:
                count = len(self.variables[var_name]) if hasattr(self.variables[var_name], '__len__') else 1
                self.variables['_last_result'] = count
                self._debug_print(f"Comptage effectué: {count} éléments")
        
        else:
            raise ValueError(f"Commande inconnue: {' '.join(tokens)}")
    
    def get_variable(self, name: str):
        """Récupère une variable"""
        return self.variables.get(name)
    
    def set_variable(self, name: str, value: Any):
        """Définit une variable"""
        self.variables[name] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interpréteur pour les fichiers .grab")
    parser.add_argument("file", help="Fichier .grab à exécuter")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug avec affichage détaillé")
    
    args = parser.parse_args()
    
    interpreter = GrabInterpreter(debug_mode=args.debug)
    interpreter.execute_file(args.file)