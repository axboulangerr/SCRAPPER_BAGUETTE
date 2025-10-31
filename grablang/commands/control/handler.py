"""
Handler principal pour la commande CONTROL
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class ControlHandler(BaseCommand):
    """Handler principal pour les structures de contrôle"""
    
    def __init__(self):
        self.debug_mode = False
        self.interpreter_ref = None  # Référence vers l'interpréteur pour exécuter des blocs
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def set_interpreter_ref(self, interpreter):
        """Définit la référence vers l'interpréteur"""
        self.interpreter_ref = interpreter
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("CONTROL", "CONTROL")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """
        Exécute les structures de contrôle
        Cette méthode sera appelée par l'interpréteur pour IF, FOR, WHILE
        """
        if not args:
            raise ValueError("CONTROL: Structure de contrôle requise (IF, FOR, WHILE)")
        
        structure_type = args[0].upper()
        remaining_args = args[1:]
        
        if structure_type == "IF":
            return self._execute_if(remaining_args, variables)
        elif structure_type == "FOR":
            return self._execute_for(remaining_args, variables)
        elif structure_type == "WHILE":
            return self._execute_while(remaining_args, variables)
        else:
            raise ValueError(f"CONTROL: Structure '{structure_type}' non supportée")
    
    def _execute_if(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """Exécute une structure IF conditionnelle"""
        # Cette méthode sera implémentée pour gérer les blocs IF
        raise NotImplementedError("Structure IF sera implémentée avec un parser de blocs")
    
    def _execute_for(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """Exécute une boucle FOR"""
        # Cette méthode sera implémentée pour gérer les boucles FOR
        raise NotImplementedError("Structure FOR sera implémentée avec un parser de blocs")
    
    def _execute_while(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """Exécute une boucle WHILE"""
        # Cette méthode sera implémentée pour gérer les boucles WHILE
        raise NotImplementedError("Structure WHILE sera implémentée avec un parser de blocs")
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Évalue une condition logique"""
        # Nettoie la condition
        condition = condition.strip()
        
        # Conditions simples supportées
        if " EXISTS" in condition:
            var_name = condition.replace(" EXISTS", "").strip()
            return var_name in variables
        
        if " NOT EXISTS" in condition:
            var_name = condition.replace(" NOT EXISTS", "").strip()
            return var_name not in variables
        
        if " NOT EMPTY" in condition:
            var_name = condition.replace(" NOT EMPTY", "").strip()
            if var_name in variables:
                value = variables[var_name]
                if hasattr(value, '__len__'):
                    return len(value) > 0
                return bool(value)
            return False
        
        if " EMPTY" in condition:
            var_name = condition.replace(" EMPTY", "").strip()
            if var_name in variables:
                value = variables[var_name]
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
                    
                    if left in variables:
                        left_value = variables[left]
                        
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