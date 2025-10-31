"""
Commande FILTER ALL pour filtrer tous les éléments selon une condition
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import re

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class FilteringAllCommand(BaseCommand):
    """Commande pour filtrer tous les éléments selon une condition WHERE"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("FILTER ALL", "FILTER")
            print(f"{colored_prefix} {message}")
    
    def _matches_condition(self, element: Tag, condition_args: List[str]) -> bool:
        """Vérifie si un élément correspond à une condition"""
        if len(condition_args) < 3:
            return False
        
        field = condition_args[0].lower()
        
        # Gestion spéciale pour les conditions de parent
        if field == "parent":
            return self._matches_parent_condition(element, condition_args[1:])
        
        operator = condition_args[1].upper()
        value = condition_args[2]
        
        # Récupère la valeur à tester selon le champ
        if field == "class":
            test_value = " ".join(element.get("class", []))
        elif field == "text":
            test_value = element.get_text(strip=True)
        elif field == "attr":
            if len(condition_args) < 4:
                return False
            attr_name = condition_args[2]
            operator = condition_args[3].upper()
            value = condition_args[4] if len(condition_args) > 4 else None
            test_value = element.get(attr_name)
        else:
            # Assume it's an attribute name
            test_value = element.get(field)
        
        # Debug pour voir les valeurs comparées
        if self.debug_mode and field == "href":
            self._debug_print(f"Test element: {element.name}, href = '{test_value}', recherche: '{value}'")
        
        # Applique l'opérateur
        if operator == "CONTAINS":
            # Nettoie la valeur recherchée (supprime les guillemets)
            clean_value = value.strip('"\'')
            result = clean_value.lower() in str(test_value).lower() if test_value else False
            if self.debug_mode and field == "href":
                self._debug_print(f"CONTAINS test: '{clean_value}' in '{test_value}' = {result}")
            return result
        elif operator == "MATCHES":
            return bool(re.search(value, str(test_value))) if test_value else False
        elif operator == "NOT" and len(condition_args) > 3 and condition_args[3].upper() == "NULL":
            return test_value is not None
        elif operator == "NULL":
            return test_value is None
        elif operator == "=":
            return str(test_value) == value if test_value else False
        elif operator == "!=":
            return str(test_value) != value if test_value else True
        
        return False
    
    def _matches_parent_condition(self, element: Tag, parent_condition_args: List[str]) -> bool:
        """Vérifie si l'élément a un parent qui correspond à la condition"""
        if len(parent_condition_args) < 4:
            return False
        
        parent_tag = parent_condition_args[0].lower()  # ex: "div"
        parent_field = parent_condition_args[1].lower()  # ex: "class"
        operator = parent_condition_args[2].upper()  # ex: "CONTAINS"
        value = parent_condition_args[3]  # ex: "group relative @sm:last:hidden @md:last:block pt-0"
        
        self._debug_print(f"Recherche parent {parent_tag} avec {parent_field} {operator} '{value}'")
        
        # Remonte dans la hiérarchie pour trouver un parent correspondant
        current = element.parent
        while current and current.name:
            self._debug_print(f"Vérification parent: {current.name}")
            
            # Vérifie si c'est le bon type de balise
            if current.name.lower() == parent_tag:
                self._debug_print(f"Parent {parent_tag} trouvé, vérification des conditions...")
                
                # Récupère la valeur à tester selon le champ
                if parent_field == "class":
                    test_value = " ".join(current.get("class", []))
                    self._debug_print(f"Classes du parent: '{test_value}'")
                elif parent_field == "id":
                    test_value = current.get("id", "")
                elif parent_field == "text":
                    test_value = current.get_text(strip=True)
                else:
                    # Attribut quelconque
                    test_value = current.get(parent_field, "")
                
                # Applique l'opérateur
                if operator == "CONTAINS":
                    # Nettoie la valeur recherchée (supprime les guillemets)
                    clean_value = value.strip('"\'')
                    result = clean_value.lower() in str(test_value).lower() if test_value else False
                    self._debug_print(f"Test CONTAINS: '{clean_value}' in '{test_value}' = {result}")
                    if result:
                        return True
                elif operator == "MATCHES":
                    result = bool(re.search(value, str(test_value))) if test_value else False
                    if result:
                        return True
                elif operator == "=":
                    result = str(test_value) == value if test_value else False
                    if result:
                        return True
            
            # Continue vers le parent suivant
            current = current.parent
        
        self._debug_print("Aucun parent correspondant trouvé")
        return False

    def execute(self, args: List[str], variables: Dict[str, Any]) -> ResultSet:
        """
        Exécute FILTER ALL WHERE condition
        
        Args:
            args: condition arguments (ex: ["class", "CONTAINS", "active"])
            variables: Variables disponibles
            
        Returns:
            ResultSet contenant tous les éléments qui correspondent à la condition
        """
        if len(args) < 3:
            raise ValueError("FILTER ALL: Condition incomplète. Exemples: class CONTAINS \"active\", text MATCHES \"^[0-9]+$\"")
        
        # Récupère les éléments à filtrer
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("FILTER ALL: Aucun élément à filtrer")
        
        elements_to_filter = []
        if isinstance(last_result, ResultSet):
            elements_to_filter = list(last_result)
        elif isinstance(last_result, Tag):
            elements_to_filter = [last_result]
        else:
            raise ValueError("FILTER ALL: Les données à filtrer doivent être des éléments HTML")
        
        self._debug_print(f"Filtrage de {len(elements_to_filter)} élément(s) avec condition: {' '.join(args)}")
        
        # Filtre les éléments
        filtered_elements = []
        for element in elements_to_filter:
            if self._matches_condition(element, args):
                filtered_elements.append(element)
        
        self._debug_print(f"{len(filtered_elements)} élément(s) correspondent à la condition")
        
        # Si debug activé, affiche un aperçu des éléments trouvés
        if self.debug_mode and filtered_elements:
            for i, elem in enumerate(filtered_elements[:3]):  # Affiche les 3 premiers
                preview = str(elem)[:200] + "..." if len(str(elem)) > 200 else str(elem)
                self._debug_print(f"  Élément {i+1}: {preview}")
            if len(filtered_elements) > 3:
                self._debug_print(f"  ... et {len(filtered_elements) - 3} autre(s)")
        
        # Retourne les éléments filtrés dans un ResultSet
        if filtered_elements:
            # Crée un ResultSet factice pour maintenir la compatibilité
            soup = BeautifulSoup("", "html.parser")
            result_set = ResultSet(soup.find, ())
            result_set.extend(filtered_elements)
            return result_set
        else:
            # Retourne un ResultSet vide
            soup = BeautifulSoup("", "html.parser")
            return ResultSet(soup.find, ())