"""
Commande EXTRACT REGEX pour extraire du contenu en utilisant des expressions régulières personnalisées
"""
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Dict, Any, Union
import sys
from pathlib import Path
import re

# Ajoute le chemin vers le module core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from base_command import BaseCommand
from colors import CommandColors

class ExtractionRegexCommand(BaseCommand):
    """Commande pour extraire du contenu en utilisant des expressions régulières personnalisées"""
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug_mode(self, debug_mode: bool):
        """Active ou désactive le mode debug"""
        self.debug_mode = debug_mode
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("EXTRACT REGEX", "EXTRACT")
            print(f"{colored_prefix} {message}")
    
    def _extract_with_regex(self, text: str, pattern: str, flags: int = 0) -> List[str]:
        """Extrait le contenu d'un texte en utilisant une expression régulière"""
        if not text or not pattern:
            return []
        
        try:
            # Compile le pattern avec les flags
            compiled_pattern = re.compile(pattern, flags)
            matches = compiled_pattern.findall(text)
            
            # Si le pattern contient des groupes de capture, on les traite
            if matches and isinstance(matches[0], tuple):
                # Si c'est des tuples (groupes multiples), on les convertit en strings
                result = []
                for match in matches:
                    if len(match) == 1:
                        result.append(match[0])
                    else:
                        # Joint les groupes avec un espace ou retourne le tuple formaté
                        result.append(' '.join(str(group) for group in match if group))
                return result
            else:
                # Retourne directement les matches si pas de groupes
                return [str(match) for match in matches]
                
        except re.error as e:
            raise ValueError(f"EXTRACT REGEX: Expression régulière invalide '{pattern}': {e}")
    
    def _parse_flags(self, flag_string: str) -> int:
        """Parse les flags regex depuis une string"""
        flags = 0
        flag_string = flag_string.upper()
        
        if 'I' in flag_string or 'IGNORECASE' in flag_string:
            flags |= re.IGNORECASE
        if 'M' in flag_string or 'MULTILINE' in flag_string:
            flags |= re.MULTILINE
        if 'S' in flag_string or 'DOTALL' in flag_string:
            flags |= re.DOTALL
        if 'X' in flag_string or 'VERBOSE' in flag_string:
            flags |= re.VERBOSE
        if 'A' in flag_string or 'ASCII' in flag_string:
            flags |= re.ASCII
        
        return flags

    def _clean_quotes(self, text: str) -> str:
        """Supprime les guillemets d'ouverture et de fermeture si présents"""
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        return text

    def execute(self, args: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Exécute EXTRACT REGEX <pattern> [flags]
        
        Args:
            args: [pattern, flags_optionnel]
                - pattern: Expression régulière à utiliser
                - flags: Flags optionnels (i, m, s, x, a) séparés par des virgules
            variables: Variables disponibles
            
        Returns:
            List[str] contenant toutes les correspondances trouvées
            
        Exemples:
            EXTRACT REGEX "\d+\.\d+" -> Extrait tous les nombres décimaux
            EXTRACT REGEX "([A-Z][a-z]+)" -> Extrait tous les mots commençant par une majuscule
            EXTRACT REGEX "email:\s*(\S+@\S+)" i -> Extrait les emails après "email:" (insensible à la casse)
            EXTRACT REGEX "\b\w+@\w+\.\w+\b" -> Extrait toutes les adresses email
            EXTRACT REGEX "(\d{1,2})/(\d{1,2})/(\d{4})" -> Extrait les dates au format MM/DD/YYYY
        """
        if not args:
            raise ValueError("EXTRACT REGEX: Pattern requis. Usage: EXTRACT REGEX <pattern> [flags]")
        
        pattern = self._clean_quotes(args[0])  # Nettoie les guillemets du pattern
        flags = 0
        
        # Parse les flags si fournis
        if len(args) > 1:
            flag_string = args[1]
            flags = self._parse_flags(flag_string)
        
        # Récupère les éléments depuis _last_result
        last_result = variables.get('_last_result')
        if last_result is None:
            raise ValueError("EXTRACT REGEX: Aucun élément à traiter")
        
        elements_to_process = []
        if isinstance(last_result, ResultSet):
            elements_to_process = list(last_result)
        elif isinstance(last_result, Tag):
            elements_to_process = [last_result]
        elif isinstance(last_result, BeautifulSoup):
            # Si c'est une page complète, on prend le body ou html
            body = last_result.body if last_result.body else last_result
            elements_to_process = [body]
        elif isinstance(last_result, list):
            # Si c'est déjà une liste (résultat d'extraction précédente), on peut la traiter
            # mais on doit la convertir en texte pour la regex
            text_content = ' '.join(str(item) for item in last_result)
            matches = self._extract_with_regex(text_content, pattern, flags)
            self._debug_print(f"Extraction sur liste précédente: {len(matches)} correspondance(s) trouvée(s)")
            return matches
        else:
            raise ValueError(f"EXTRACT REGEX: Type de données non supporté: {type(last_result).__name__}. Les données doivent être des éléments HTML")
        
        self._debug_print(f"Extraction avec regex '{pattern}' sur {len(elements_to_process)} élément(s)")
        if flags:
            flag_names = []
            if flags & re.IGNORECASE: flag_names.append("IGNORECASE")
            if flags & re.MULTILINE: flag_names.append("MULTILINE")
            if flags & re.DOTALL: flag_names.append("DOTALL")
            if flags & re.VERBOSE: flag_names.append("VERBOSE")
            if flags & re.ASCII: flag_names.append("ASCII")
            self._debug_print(f"Flags utilisés: {', '.join(flag_names)}")
        
        # Extrait toutes les correspondances de tous les éléments
        all_matches = []
        for element in elements_to_process:
            text = element.get_text()
            matches = self._extract_with_regex(text, pattern, flags)
            all_matches.extend(matches)
        
        self._debug_print(f"{len(all_matches)} correspondance(s) trouvée(s)")
        
        # Si debug activé, affiche un aperçu des correspondances
        if self.debug_mode and all_matches:
            preview_count = min(5, len(all_matches))
            self._debug_print(f"  Correspondances trouvées (premières {preview_count}):")
            for i, match in enumerate(all_matches[:preview_count]):
                preview_match = match[:100] + "..." if len(match) > 100 else match
                self._debug_print(f"    {i+1}. '{preview_match}'")
            if len(all_matches) > 5:
                self._debug_print(f"  ... et {len(all_matches) - 5} autre(s)")
        
        return all_matches