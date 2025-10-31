"""
Exécuteur pour les scripts GrabLang
Responsable de l'exécution de l'AST généré par le parser
"""
from typing import Dict, Any, List
from pathlib import Path
import importlib.util

from .parser import ASTNode
from ..utils.colors import CommandColors


class GrabLangExecutor:
    """Exécuteur principal pour les AST GrabLang"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.variables = {}
        self.commands = {}
        self._load_commands()
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXECUTOR", "DEBUG")
            print(f"{colored_prefix} {message}")
    
    def execute(self, ast: ASTNode) -> None:
        """
        Exécute un AST GrabLang complet
        
        Args:
            ast: L'arbre syntaxique abstrait à exécuter
        """
        self._debug_print("Début de l'exécution de l'AST")
        
        if ast.type == "PROGRAM":
            for statement in ast.children:
                self._execute_statement(statement)
        else:
            self._execute_statement(ast)
        
        self._debug_print("Exécution de l'AST terminée")
    
    def _execute_statement(self, node: ASTNode) -> Any:
        """
        Exécute une instruction
        
        Args:
            node: Nœud AST représentant l'instruction
            
        Returns:
            Le résultat de l'exécution
        """
        try:
            if node.type == "COMMAND":
                return self._execute_command(node)
            elif node.type == "IF_STATEMENT":
                return self._execute_if_statement(node)
            elif node.type == "FOR_STATEMENT":
                return self._execute_for_statement(node)
            elif node.type == "WHILE_STATEMENT":
                return self._execute_while_statement(node)
            elif node.type == "BLOCK":
                return self._execute_block(node)
            else:
                raise ValueError(f"Type de nœud non supporté: {node.type}")
                
        except Exception as e:
            print(f"Erreur ligne {node.line_number}: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            raise
    
    def _execute_command(self, node: ASTNode) -> Any:
        """
        Exécute une commande
        
        Args:
            node: Nœud AST représentant la commande
            
        Returns:
            Le résultat de la commande
        """
        command_name = node.value.upper()
        args = []
        
        # Extrait les arguments de la commande
        for arg_node in node.children:
            if arg_node.type == "STRING_LITERAL":
                args.append(f'"{arg_node.value}"')  # Remet les guillemets pour compatibilité
            elif arg_node.type == "IDENTIFIER":
                args.append(arg_node.value)
            elif arg_node.type == "OPERATOR":
                # Support des opérateurs comme WHERE, CONTAINS, etc.
                args.append(arg_node.value)
        
        self._debug_print(f"Exécution de la commande {command_name} avec arguments: {args}")
        
        # Détermine la clé de commande appropriée
        command_key = self._resolve_command_key(command_name, args)
        
        if command_key and command_key in self.commands:
            # Gestion spéciale pour certaines commandes avec alias
            if command_key in ["SAVE", "USE", "COUNT", "JSON"]:
                args = [command_key] + args
            
            # Exécute la commande
            result = self.commands[command_key].execute(args, self.variables)
            
            # Stocke le résultat
            if result is not None:
                self.variables['_last_result'] = result
                self._debug_print(f"Résultat stocké dans _last_result (type: {type(result).__name__})")
            
            return result
        else:
            raise ValueError(f"Commande inconnue: {command_name} {' '.join(args)}")
    
    def _execute_if_statement(self, node: ASTNode) -> None:
        """Exécute une structure IF"""
        if len(node.children) < 2:
            raise ValueError("IF: Structure incomplète")
        
        condition_node = node.children[0]
        block_node = node.children[1]
        
        condition_result = self._evaluate_condition(condition_node)
        
        self._debug_print(f"Condition IF: {condition_node.value} = {condition_result}")
        
        if condition_result:
            self._execute_statement(block_node)
        else:
            self._debug_print("Condition IF fausse, bloc ignoré")
    
    def _execute_for_statement(self, node: ASTNode) -> None:
        """Exécute une boucle FOR"""
        if len(node.children) < 2:
            raise ValueError("FOR: Structure incomplète")
        
        for_condition_node = node.children[0]
        block_node = node.children[1]
        
        # Extrait les informations de la condition FOR
        if len(for_condition_node.children) < 2:
            raise ValueError("FOR: Condition incomplète")
        
        var_node = for_condition_node.children[0]
        source_node = for_condition_node.children[1]
        
        var_name = var_node.value
        
        # Détermine la source d'itération
        if source_node.type == "RANGE":
            # RANGE avec un nombre ou une variable
            try:
                range_value = int(source_node.value)
            except ValueError:
                # C'est une variable
                if source_node.value in self.variables:
                    range_value = int(self.variables[source_node.value])
                else:
                    raise ValueError(f"FOR: Variable '{source_node.value}' non trouvée pour RANGE")
            
            items = list(range(range_value))
        else:
            # Variable existante
            if source_node.value in self.variables:
                items = self.variables[source_node.value]
                if not hasattr(items, '__iter__'):
                    items = [items]
            else:
                raise ValueError(f"FOR: Variable '{source_node.value}' non trouvée")
        
        self._debug_print(f"Boucle FOR sur {len(items)} élément(s)")
        
        # Exécute le bloc pour chaque élément
        for i, item in enumerate(items):
            self.variables[var_name] = item
            self.variables[f"{var_name}_index"] = i
            
            self._debug_print(f"FOR iteration {i}: {var_name} = {item}")
            
            self._execute_statement(block_node)
    
    def _execute_while_statement(self, node: ASTNode) -> None:
        """Exécute une boucle WHILE"""
        if len(node.children) < 2:
            raise ValueError("WHILE: Structure incomplète")
        
        condition_node = node.children[0]
        block_node = node.children[1]
        
        iteration = 0
        max_iterations = 1000  # Protection contre les boucles infinies
        
        while self._evaluate_condition(condition_node) and iteration < max_iterations:
            self._debug_print(f"WHILE iteration {iteration}: condition vraie")
            
            self._execute_statement(block_node)
            
            iteration += 1
        
        if iteration >= max_iterations:
            print(f"Attention: Boucle WHILE interrompue après {max_iterations} itérations")
        else:
            self._debug_print(f"WHILE terminée après {iteration} itération(s)")
    
    def _execute_block(self, node: ASTNode) -> None:
        """Exécute un bloc de code"""
        for statement in node.children:
            self._execute_statement(statement)
    
    def _evaluate_condition(self, condition_node: ASTNode) -> bool:
        """
        Évalue une condition logique
        
        Args:
            condition_node: Nœud AST représentant la condition
            
        Returns:
            bool: Résultat de l'évaluation
        """
        condition = condition_node.value.strip()
        
        # Conditions simples supportées
        if " EXISTS" in condition:
            var_name = condition.replace(" EXISTS", "").strip()
            return var_name in self.variables
        
        if " NOT EXISTS" in condition:
            var_name = condition.replace(" NOT EXISTS", "").strip()
            return var_name not in self.variables
        
        if " NOT EMPTY" in condition:
            var_name = condition.replace(" NOT EMPTY", "").strip()
            if var_name in self.variables:
                value = self.variables[var_name]
                if hasattr(value, '__len__'):
                    return len(value) > 0
                return bool(value)
            return False
        
        if " EMPTY" in condition:
            var_name = condition.replace(" EMPTY", "").strip()
            if var_name in self.variables:
                value = self.variables[var_name]
                if hasattr(value, '__len__'):
                    return len(value) == 0
                return not bool(value)
            return True
        
        # Comparaisons avec valeurs
        for op in [" EQUALS ", " CONTAINS ", " GREATER ", " LESS "]:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip('"\'')
                    
                    if left in self.variables:
                        left_value = self.variables[left]
                        
                        if op == " EQUALS ":
                            return str(left_value) == right
                        elif op == " CONTAINS ":
                            return right in str(left_value)
                        elif op == " GREATER ":
                            try:
                                return float(left_value) > float(right)
                            except:
                                return len(str(left_value)) > len(right)
                        elif op == " LESS ":
                            try:
                                return float(left_value) < float(right)
                            except:
                                return len(str(left_value)) < len(right)
        
        # Si aucune condition reconnue, retourne False
        return False
    
    def _resolve_command_key(self, command_name: str, args: List[str]) -> str:
        """
        Résout la clé de commande appropriée basée sur le nom et les arguments
        
        Args:
            command_name: Nom de la commande
            args: Arguments de la commande
            
        Returns:
            str: Clé de commande à utiliser
        """
        # Gestion spéciale pour FILTER avec WHERE
        if command_name == "FILTER" and len(args) >= 2 and "WHERE" in [arg.upper() for arg in args]:
            return "FILTER"
        
        # Essaie les commandes composées à 3 mots (GET ATTR FIRST)
        if len(args) >= 2:
            potential_key = f"{command_name}_{args[0].upper()}_{args[1].upper()}"
            if command_name == "GET" and potential_key.replace("GET_", "") in self._get_getter_subcommands():
                return command_name
        
        # Essaie les commandes composées à 2 mots (LOAD URL)
        if len(args) >= 1:
            potential_key = f"{command_name}_{args[0].upper()}"
            if potential_key in self.commands:
                return potential_key
        
        # Commande simple
        if command_name in self.commands:
            return command_name
        
        return None
    
    def _get_getter_subcommands(self):
        """Récupère la liste des sous-commandes GET disponibles"""
        if "GET" in self.commands and hasattr(self.commands["GET"], "subcommands"):
            return self.commands["GET"].subcommands.keys()
        return []
    
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
                elif command_key == "UTILITIES":
                    self.commands["SAVE"] = handler_instance
                    self.commands["USE"] = handler_instance
                    self.commands["COUNT"] = handler_instance
                    self.commands["JSON"] = handler_instance
                elif command_key == "GETTER":
                    self.commands["GET"] = handler_instance
                elif command_key == "FILTERING":
                    self.commands["FILTER"] = handler_instance
                elif command_key == "EXTRACTION":
                    self.commands["EXTRACT"] = handler_instance
                
        except Exception as e:
            self._debug_print(f"Erreur lors du chargement du handler {category}: {e}")
    
    def get_variable(self, name: str):
        """Récupère une variable"""
        return self.variables.get(name)
    
    def set_variable(self, name: str, value: Any):
        """Définit une variable"""
        self.variables[name] = value