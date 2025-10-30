"""
Classe de base pour toutes les commandes
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCommand(ABC):
    """Classe de base pour toutes les commandes du langage .grab"""
    
    @abstractmethod
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Any:
        """
        Exécute la commande avec les arguments fournis
        
        Args:
            args: Liste des arguments de la commande
            variables: Dictionnaire des variables disponibles
            
        Returns:
            Le résultat de la commande (peut être None)
        """
        pass
    
    def validate_args(self, args: List[str], expected_count: int, command_name: str):
        """Valide le nombre d'arguments"""
        if len(args) != expected_count:
            raise ValueError(f"Commande {command_name}: attendu {expected_count} argument(s), reçu {len(args)}")
    
    def resolve_variable(self, value: str, variables: Dict[str, Any]) -> Any:
        """Résout une variable ou retourne la valeur littérale"""
        if value in variables:
            return variables[value]
        return value