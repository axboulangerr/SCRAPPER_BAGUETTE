"""
Commande GET ATTR pour extraire les attributs des éléments HTML
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import sys
from pathlib import Path

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class GetterAttrCommand(BaseCommand):
    """Commande pour extraire les attributs des éléments HTML sélectionnés"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("GET ATTR", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> Union[str, List[str]]:
        """
        Exécute GET ATTR "attribute_name"
        
        Args:
            args: [attribute_name] - Le nom de l'attribut à extraire
            variables: Variables disponibles
            
        Returns:
            str pour un seul élément, List[str] pour plusieurs éléments
        """
        self.validate_args(args, 1, "GET ATTR")
        
        attribute_name = args[0]
        last_result = variables['_last_result']
        
        self._debug_print(f"Extraction de l'attribut '{attribute_name}'")
        
        # Cas d'un seul élément (Tag)
        if isinstance(last_result, Tag):
            attr_value = last_result.get(attribute_name)
            if attr_value is None:
                self._debug_print(f"⚠️ Attribut '{attribute_name}' non trouvé dans l'élément")
                return None
            
            # Gère les attributs multiples (comme class)
            if isinstance(attr_value, list):
                attr_value = " ".join(attr_value)
            
            self._debug_print(f"Attribut '{attribute_name}': {attr_value}")
            return attr_value
        
        # Cas de plusieurs éléments (ResultSet ou list)
        elif isinstance(last_result, (ResultSet, list)):
            attributes = []
            found_count = 0
            
            for element in last_result:
                if isinstance(element, Tag):
                    attr_value = element.get(attribute_name)
                    if attr_value is not None:
                        # Gère les attributs multiples (comme class)
                        if isinstance(attr_value, list):
                            attr_value = " ".join(attr_value)
                        attributes.append(attr_value)
                        found_count += 1
                    else:
                        # Ajoute None pour maintenir l'ordre
                        attributes.append(None)
            
            # Filtre les None si on veut seulement les valeurs existantes
            clean_attributes = [attr for attr in attributes if attr is not None]
            
            self._debug_print(f"{found_count} attribut(s) '{attribute_name}' trouvé(s) sur {len(last_result)} élément(s)")
            
            return clean_attributes if clean_attributes else []
        
        else:
            raise ValueError(f"GET ATTR: Type de données non supporté: {type(last_result).__name__}")