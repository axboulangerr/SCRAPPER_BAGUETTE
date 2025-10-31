"""
Handler principal pour la commande PRINT
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup, Tag, ResultSet

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class PrintHandler(BaseCommand):
    """Handler principal pour la commande PRINT"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("PRINT", "PRINT")
            print(f"{colored_prefix} {message}")
    
    def _format_value_normal(self, value: Any, variable_name: str) -> str:
        """Formate une valeur pour l'affichage normal"""
        if isinstance(value, BeautifulSoup):
            title = value.title.string if value.title else "Sans titre"
            return f"Page HTML '{variable_name}': {title}"
        
        elif isinstance(value, ResultSet):
            count = len(value)
            if count == 0:
                return f"Résultat vide '{variable_name}': Aucun élément"
            else:
                first_tag = value[0].name if value else "inconnu"
                return f"Résultat '{variable_name}': {count} élément(s) <{first_tag}>"
        
        elif isinstance(value, Tag):
            tag_name = value.name
            classes = value.get('class', [])
            class_str = f".{'.'.join(classes)}" if classes else ""
            text_preview = value.get_text(strip=True)[:50] + "..." if len(value.get_text(strip=True)) > 50 else value.get_text(strip=True)
            return f"Élément '{variable_name}': <{tag_name}{class_str}> '{text_preview}'"
        
        elif isinstance(value, list):
            return f"Liste '{variable_name}': {len(value)} élément(s)"
        
        elif isinstance(value, str):
            preview = value[:100] + "..." if len(value) > 100 else value
            return f"Texte '{variable_name}': '{preview}'"
        
        else:
            return f"Variable '{variable_name}': {type(value).__name__} = {str(value)[:100]}"
    
    def _format_value_dev(self, value: Any, variable_name: str) -> str:
        """Formate une valeur pour l'affichage développeur détaillé"""
        result = []
        
        # En-tête avec type
        result.append(f"DEV - Variable '{variable_name}' ({type(value).__name__}):")
        
        if isinstance(value, BeautifulSoup):
            title = value.title.string if value.title else "Sans titre"
            result.append(f"   Type: Page HTML complète")
            result.append(f"   Titre: {title}")
            result.append(f"   Taille: {len(str(value))} caractères")
            result.append(f"   Éléments principaux:")
            
            # Compte les éléments principaux
            for tag in ['div', 'span', 'a', 'p', 'img', 'h1', 'h2', 'h3']:
                count = len(value.find_all(tag))
                if count > 0:
                    result.append(f"     - {tag}: {count}")
        
        elif isinstance(value, ResultSet):
            count = len(value)
            result.append(f"   Type: Résultat de sélection")
            result.append(f"   Nombre d'éléments: {count}")
            
            if count > 0:
                # Analyse des types d'éléments
                tag_counts = {}
                for elem in value:
                    tag_name = elem.name
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
                
                result.append(f"   Types d'éléments:")
                for tag, count in tag_counts.items():
                    result.append(f"     - <{tag}>: {count}")
                
                # Aperçu des premiers éléments
                result.append(f"   Aperçu (3 premiers):")
                for i, elem in enumerate(value[:3]):
                    classes = elem.get('class', [])
                    class_str = f".{'.'.join(classes)}" if classes else ""
                    text = elem.get_text(strip=True)[:30] + "..." if len(elem.get_text(strip=True)) > 30 else elem.get_text(strip=True)
                    result.append(f"     {i+1}. <{elem.name}{class_str}> '{text}'")
        
        elif isinstance(value, Tag):
            result.append(f"   Type: Élément HTML unique")
            result.append(f"   Balise: <{value.name}>")
            
            # Attributs
            attrs = dict(value.attrs) if value.attrs else {}
            if attrs:
                result.append(f"   Attributs:")
                for attr, val in attrs.items():
                    val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                    result.append(f"     - {attr}: {val_str}")
            
            # Contenu textuel
            text = value.get_text(strip=True)
            if text:
                text_preview = text[:100] + "..." if len(text) > 100 else text
                result.append(f"   Texte: '{text_preview}'")
            
            # Enfants
            children = [child for child in value.children if hasattr(child, 'name')]
            if children:
                result.append(f"   Enfants: {len(children)} élément(s)")
        
        elif isinstance(value, list):
            result.append(f"   Type: Liste Python")
            result.append(f"   Nombre d'éléments: {len(value)}")
            if value:
                result.append(f"   Types des éléments:")
                type_counts = {}
                for item in value:
                    type_name = type(item).__name__
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1
                for type_name, count in type_counts.items():
                    result.append(f"     - {type_name}: {count}")
        
        elif isinstance(value, str):
            result.append(f"   Type: Chaîne de caractères")
            result.append(f"   Longueur: {len(value)} caractères")
            if len(value) > 200:
                result.append(f"   Aperçu: '{value[:200]}...'")
            else:
                result.append(f"   Contenu: '{value}'")
        
        else:
            result.append(f"   Type: {type(value).__name__}")
            result.append(f"   Valeur: {str(value)}")
        
        return "\n".join(result)
    
    def _is_string_literal(self, text: str) -> bool:
        """Vérifie si le texte est une chaîne littérale (entre guillemets)"""
        return (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'"))
    
    def _extract_string_content(self, text: str) -> str:
        """Extrait le contenu d'une chaîne littérale (supprime les guillemets)"""
        if self._is_string_literal(text):
            return text[1:-1]  # Supprime le premier et dernier caractère (guillemets)
        return text

    def execute(self, args: List[str], variables: Dict[str, Any]) -> None:
        """
        Exécute la commande PRINT
        
        Args:
            args: [variable_name_ou_string] ou [DEV, variable_name]
            variables: Variables disponibles
        """
        if len(args) < 1 or len(args) > 2:
            raise ValueError("PRINT: Utilisez PRINT variable_name, PRINT \"texte\" ou PRINT DEV variable_name")
        
        # Détermine le mode (normal ou DEV)
        dev_mode = False
        if len(args) == 2:
            if args[0].upper() == "DEV":
                dev_mode = True
                target = args[1]
            else:
                raise ValueError("PRINT: Format incorrect. Utilisez PRINT variable_name, PRINT \"texte\" ou PRINT DEV variable_name")
        else:
            target = args[0]
        
        # Vérifie si c'est une chaîne littérale
        if self._is_string_literal(target):
            # C'est une chaîne littérale - affichage direct
            string_content = self._extract_string_content(target)
            self._debug_print(f"Affichage de la chaîne littérale: '{string_content}'")
            
            # Affiche le résultat avec une couleur spéciale pour PRINT
            colored_prefix = CommandColors.colorize_prefix("PRINT", "PRINT")
            print(f"{colored_prefix} {string_content}")
            return
        
        # C'est une variable - comportement original
        variable_name = target
        self._debug_print(f"Affichage de la variable '{variable_name}' (mode {'DEV' if dev_mode else 'normal'})")
        
        # Vérifie que la variable existe
        if variable_name not in variables:
            # Liste les variables disponibles (exclut les variables internes)
            available_vars = [name for name in variables.keys() if not name.startswith('_')]
            if available_vars:
                available_str = ", ".join(available_vars)
                raise ValueError(f"PRINT: Variable '{variable_name}' non trouvée. Variables disponibles: {available_str}")
            else:
                raise ValueError(f"PRINT: Variable '{variable_name}' non trouvée. Aucune variable disponible.")
        
        # Récupère et affiche la valeur
        value = variables[variable_name]
        
        if dev_mode:
            output = self._format_value_dev(value, variable_name)
        else:
            output = self._format_value_normal(value, variable_name)
        
        # Affiche le résultat avec une couleur spéciale pour PRINT
        colored_prefix = CommandColors.colorize_prefix("PRINT", "PRINT")
        print(f"{colored_prefix} {output}")