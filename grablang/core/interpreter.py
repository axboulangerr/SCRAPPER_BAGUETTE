"""
Interpréteur principal pour les fichiers .grab
Coordonne le parsing et l'exécution des scripts GrabLang
"""
import argparse
from pathlib import Path

from .parser import GrabLangParser
from .executor import GrabLangExecutor
from ..utils.colors import CommandColors


class GrabInterpreter:
    """Interpréteur principal coordonnant parser et exécuteur"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.parser = GrabLangParser(debug_mode=debug_mode)
        self.executor = GrabLangExecutor(debug_mode=debug_mode)
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug avec couleur"""
        if self.debug_mode:
            colored_prefix = CommandColors.colorize_prefix("INTERPRETER", "DEBUG")
            print(f"{colored_prefix} {message}")
    
    def execute_file(self, file_path: str):
        """
        Exécute un fichier .grab
        
        Args:
            file_path: Chemin vers le fichier à exécuter
        """
        self._debug_print(f"Lecture du fichier: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la lecture du fichier: {e}")
        
        self._debug_print(f"Contenu du fichier ({len(content)} caractères)")
        if self.debug_mode:
            for i, line in enumerate(content.split('\n'), 1):
                print(f"  {i:2d}: {line}")
        
        self.execute_script(content)
    
    def execute_script(self, script: str):
        """
        Exécute un script .grab
        
        Args:
            script: Code source du script à exécuter
        """
        self._debug_print("Début de l'interprétation du script")
        
        try:
            # Phase 1: Parsing - Analyse syntaxique
            self._debug_print("Phase 1: Parsing du script")
            ast = self.parser.parse(script)
            
            # Phase 2: Exécution - Interprétation de l'AST
            self._debug_print("Phase 2: Exécution de l'AST")
            self.executor.execute(ast)
            
            self._debug_print("Interprétation terminée avec succès")
            
        except SyntaxError as e:
            print(f"Erreur de syntaxe: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"Erreur d'exécution: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def get_variable(self, name: str):
        """Récupère une variable de l'exécuteur"""
        return self.executor.get_variable(name)
    
    def set_variable(self, name: str, value):
        """Définit une variable dans l'exécuteur"""
        self.executor.set_variable(name, value)
    
    @property
    def variables(self):
        """Accès aux variables de l'exécuteur"""
        return self.executor.variables


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interpréteur pour les fichiers .grab")
    parser.add_argument("file", help="Fichier .grab à exécuter")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug avec affichage détaillé")
    
    args = parser.parse_args()
    
    interpreter = GrabInterpreter(debug_mode=args.debug)
    interpreter.execute_file(args.file)