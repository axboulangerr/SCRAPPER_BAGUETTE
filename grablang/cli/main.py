#!/usr/bin/env python3
"""
Interface en ligne de commande pour GrabLang
"""

import argparse
import sys
from pathlib import Path
from grablang.core.interpreter import GrabInterpreter


def main():
    """Point d'entrée principal de la CLI"""
    parser = argparse.ArgumentParser(
        description="GrabLang - Interpréteur pour le web scraping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  grablang script.grab                    # Exécute un script
  grablang script.grab --debug            # Mode debug
  grablang --version                      # Affiche la version
        """
    )
    
    parser.add_argument(
        "file", 
        nargs='?',
        help="Fichier .grab à exécuter"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Active le mode debug avec affichage détaillé"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="GrabLang 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Vérifie qu'un fichier a été fourni
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    # Vérifie que le fichier existe
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Erreur: Le fichier '{args.file}' n'existe pas.")
        sys.exit(1)
    
    # Vérifie l'extension du fichier
    if file_path.suffix != '.grab':
        print(f"Attention: Le fichier ne semble pas être un script GrabLang (.grab)")
    
    try:
        # Crée et lance l'interpréteur
        interpreter = GrabInterpreter(debug_mode=args.debug)
        interpreter.execute_file(str(file_path))
        
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()