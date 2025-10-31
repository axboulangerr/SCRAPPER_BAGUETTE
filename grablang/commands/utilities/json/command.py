"""
Commande JSON pour convertir le contenu en format JSON
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import json
from pathlib import Path

# Import absolu vers le module utils du package grablang
from grablang.utils.base_command import BaseCommand
from grablang.utils.colors import CommandColors

class UtilitiesJsonCommand(BaseCommand):
    """Commande pour convertir des données en format JSON"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("JSON", "JSON")
            print(f"{colored_prefix} {message}")
    
    def execute(self, args: List[str], variables: Dict[str, Any]) -> str:
        """
        Exécute JSON [variable_name] [PRETTY|ARRAY|OBJECT] [output_filename]
        
        Args:
            args: Arguments
                  - [variable_name] : La variable à convertir (défaut: _last_result)
                  - [PRETTY] : Formatage indenté
                  - [ARRAY] : Force la conversion en array JSON
                  - [OBJECT] : Force la conversion en objet JSON avec clés numériques
                  - [output_filename] : Nom du fichier JSON à créer (optionnel)
            variables: Variables disponibles
            
        Returns:
            str - Le chemin du fichier JSON créé
        """
        # Parse des arguments
        var_name = "_last_result"
        pretty = False
        force_array = False
        force_object = False
        output_filename = None
        
        # Analyse des arguments dans l'ordre
        remaining_args = []
        for arg in args:
            if arg.upper() == "PRETTY":
                pretty = True
            elif arg.upper() == "ARRAY":
                force_array = True
            elif arg.upper() == "OBJECT":
                force_object = True
            else:
                remaining_args.append(arg)
        
        # Le premier argument restant est le nom de variable
        if len(remaining_args) >= 1:
            var_name = remaining_args[0]
        
        # Le deuxième argument restant est le nom du fichier
        if len(remaining_args) >= 2:
            filename_arg = remaining_args[1]
            
            # Vérifie si c'est un nom direct (avec guillemets) ou une variable
            if filename_arg.startswith('"') and filename_arg.endswith('"'):
                # Nom direct : retire les guillemets
                output_filename = filename_arg[1:-1]  # Enlève les guillemets
                self._debug_print(f"Nom de fichier direct: '{output_filename}'")
            elif filename_arg.startswith("'") and filename_arg.endswith("'"):
                # Nom direct avec apostrophes : retire les apostrophes
                output_filename = filename_arg[1:-1]  # Enlève les apostrophes
                self._debug_print(f"Nom de fichier direct: '{output_filename}'")
            else:
                # Variable : récupère la valeur de la variable
                if filename_arg in variables:
                    output_filename = str(variables[filename_arg])
                    self._debug_print(f"Nom de fichier depuis variable '{filename_arg}': '{output_filename}'")
                else:
                    available_vars = [name for name in variables.keys() if not name.startswith('_')]
                    if available_vars:
                        available_str = ", ".join(available_vars)
                        raise ValueError(f"JSON: Variable de nom de fichier '{filename_arg}' non trouvée. Variables disponibles: {available_str}")
                    else:
                        raise ValueError(f"JSON: Variable de nom de fichier '{filename_arg}' non trouvée. Aucune variable disponible.")
        
        # Si pas de nom de fichier spécifié, utilise le nom de la variable
        if output_filename is None:
            # Utilise le nom de la variable, en excluant les variables système
            if var_name == "_last_result":
                output_filename = "output"
            else:
                output_filename = var_name
        
        # Remplace les espaces par des underscores dans le nom de fichier
        output_filename = output_filename.replace(' ', '_')
        self._debug_print(f"Nom de fichier après nettoyage des espaces: '{output_filename}'")
        
        # Assure-toi que le nom de fichier a l'extension .json
        if not output_filename.endswith('.json'):
            output_filename += '.json'
        
        # Récupère les données à convertir
        if var_name not in variables:
            available_vars = [name for name in variables.keys() if not name.startswith('_')]
            if available_vars:
                available_str = ", ".join(available_vars)
                raise ValueError(f"JSON: Variable '{var_name}' non trouvée. Variables disponibles: {available_str}")
            else:
                raise ValueError(f"JSON: Variable '{var_name}' non trouvée. Aucune variable disponible.")
        
        data = variables[var_name]
        
        self._debug_print(f"Conversion en JSON de '{var_name}' (type: {type(data).__name__})")
        
        # Convertit les données en structure JSON
        json_data = self._convert_to_json_structure(data, force_array, force_object)
        
        # Génère le JSON
        if pretty:
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        else:
            json_str = json.dumps(json_data, ensure_ascii=False)
        
        # Écrit le fichier JSON
        output_path = Path(output_filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            self._debug_print(f"Fichier JSON créé: {output_path.absolute()} ({len(json_str)} caractères)")
            
            # Retourne le chemin du fichier créé
            return str(output_path.absolute())
            
        except Exception as e:
            raise ValueError(f"JSON: Impossible d'écrire le fichier '{output_filename}': {e}")
    
    def _convert_to_json_structure(self, data: Any, force_array: bool = False, force_object: bool = False) -> Union[Dict, List, str, int, float, bool, None]:
        """Convertit les données en structure compatible JSON"""
        
        if data is None:
            return None
        
        # Types déjà compatibles JSON
        elif isinstance(data, (str, int, float, bool)):
            return data
        
        # Listes et résultats BeautifulSoup
        elif isinstance(data, (list, ResultSet)):
            if force_object:
                # Convertit en objet avec clés numériques
                return {str(i): self._convert_element_to_json(item) for i, item in enumerate(data)}
            else:
                # Convertit en array
                return [self._convert_element_to_json(item) for item in data]
        
        # Dictionnaires
        elif isinstance(data, dict):
            return {str(k): self._convert_to_json_structure(v) for k, v in data.items()}
        
        # Éléments HTML individuels
        elif isinstance(data, (Tag, BeautifulSoup)):
            return self._convert_element_to_json(data)
        
        # Autres types itérables
        elif hasattr(data, '__iter__'):
            try:
                items = list(data)
                if force_object:
                    return {str(i): self._convert_element_to_json(item) for i, item in enumerate(items)}
                else:
                    return [self._convert_element_to_json(item) for item in items]
            except:
                return str(data)
        
        # Par défaut, convertit en string
        else:
            return str(data)
    
    def _convert_element_to_json(self, element: Any) -> Union[Dict, str]:
        """Convertit un élément (potentiellement HTML) en structure JSON"""
        
        if isinstance(element, Tag):
            # Extrait les informations importantes de l'élément HTML
            result = {
                "tag": element.name,
                "text": element.get_text(strip=True)
            }
            
            # Ajoute les attributs s'ils existent
            if element.attrs:
                result["attributes"] = element.attrs
            
            # Ajoute les liens href s'il y en a
            if element.name == "a" and element.get("href"):
                result["href"] = element.get("href")
            
            # Ajoute les sources d'images
            if element.name == "img" and element.get("src"):
                result["src"] = element.get("src")
            
            return result
        
        elif isinstance(element, BeautifulSoup):
            # Pour un document complet, extrait le titre et le contenu
            title_tag = element.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "Sans titre"
            
            return {
                "document_title": title,
                "content_length": len(str(element)),
                "text_content": element.get_text(strip=True)[:500] + "..." if len(element.get_text(strip=True)) > 500 else element.get_text(strip=True)
            }
        
        # Pour les autres types, convertit en string
        else:
            return str(element)