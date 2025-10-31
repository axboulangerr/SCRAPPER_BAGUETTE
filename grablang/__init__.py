"""
GrabLang - Un mini-langage d'interprétation dédié au web scraping
"""

__version__ = "0.1.0"
__author__ = "Votre Nom"
__description__ = "Un DSL pour le web scraping avec BeautifulSoup4"

from .core.interpreter import GrabInterpreter

__all__ = ['GrabInterpreter']