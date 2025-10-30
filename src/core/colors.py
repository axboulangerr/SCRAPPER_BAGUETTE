"""
Module de gestion des couleurs pour l'affichage terminal
"""

class Colors:
    """Codes de couleur ANSI pour le terminal"""
    
    # Couleurs de base
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Couleurs de texte
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Couleurs vives
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

class CommandColors:
    """Attribution des couleurs par type de commande"""
    
    # Couleurs pour chaque type de commande
    COLORS = {
        'DEBUG': Colors.BRIGHT_BLACK,      # Gris pour les messages debug généraux
        'LOAD': Colors.BRIGHT_BLUE,        # Bleu vif pour les commandes de chargement
        'LOAD URL': Colors.BLUE,           # Bleu normal pour LOAD URL spécifiquement
        'SELECT': Colors.BRIGHT_GREEN,     # Vert vif pour les commandes de sélection
        'SELECT ALL': Colors.GREEN,        # Vert normal pour SELECT ALL
        'SELECT FIRST': Colors.CYAN,       # Cyan pour SELECT FIRST
        'SELECT LAST': Colors.BRIGHT_CYAN, # Cyan vif pour SELECT LAST
        'SELECT ONCE': Colors.MAGENTA,     # Magenta pour SELECT ONCE
        'GET': Colors.YELLOW,              # Jaune pour les commandes GET
        'GET ATTR': Colors.BRIGHT_YELLOW,  # Jaune vif pour GET ATTR
        'GET DATE': Colors.YELLOW,         # Jaune pour GET DATE
        'EXTRACT': Colors.YELLOW,          # Jaune pour les extractions
        'FILTER': Colors.BRIGHT_YELLOW,    # Jaune vif pour les filtres
        'SAVE': Colors.BRIGHT_MAGENTA,     # Magenta vif pour les sauvegardes
        'ERROR': Colors.BRIGHT_RED,        # Rouge vif pour les erreurs
        'SUCCESS': Colors.BRIGHT_GREEN,    # Vert vif pour les succès
    }
    
    @classmethod
    def get_color(cls, command_type: str) -> str:
        """Récupère la couleur pour un type de commande"""
        return cls.COLORS.get(command_type.upper(), Colors.WHITE)
    
    @classmethod
    def colorize(cls, text: str, command_type: str) -> str:
        """Applique la couleur à un texte pour un type de commande"""
        color = cls.get_color(command_type)
        return f"{color}{text}{Colors.RESET}"
    
    @classmethod
    def colorize_prefix(cls, prefix: str, command_type: str) -> str:
        """Applique la couleur à un préfixe de commande"""
        color = cls.get_color(command_type)
        return f"{color}[{prefix}]{Colors.RESET}"