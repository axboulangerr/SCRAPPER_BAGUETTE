"""
Parser pour les scripts GrabLang
Responsable de l'analyse syntaxique et de la construction de l'AST
"""
import re
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Types de tokens reconnus par le parser"""
    COMMAND = "COMMAND"
    SUBCOMMAND = "SUBCOMMAND"
    ARGUMENT = "ARGUMENT"
    STRING = "STRING"
    VARIABLE = "VARIABLE"
    OPERATOR = "OPERATOR"
    CONTROL = "CONTROL"
    BRACE_OPEN = "BRACE_OPEN"
    BRACE_CLOSE = "BRACE_CLOSE"


@dataclass
class Token:
    """Représente un token dans le code source"""
    type: TokenType
    value: str
    line_number: int
    column: int


@dataclass
class ASTNode:
    """Nœud de l'arbre syntaxique abstrait"""
    type: str
    value: Any = None
    children: List['ASTNode'] = None
    line_number: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class GrabLangParser:
    """Parser principal pour les scripts GrabLang"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.tokens = []
        self.current_token_index = 0
        
        # Mots-clés reconnus
        self.control_keywords = {"IF", "FOR", "WHILE", "ELSE", "ELIF"}
        self.command_keywords = {"LOAD", "SELECT", "FILTER", "GET", "PRINT", "SAVE", "USE", "COUNT", "JSON", "EXTRACT"}
        self.operators = {"EXISTS", "NOT EXISTS", "EMPTY", "NOT EMPTY", "EQUALS", "CONTAINS", "GREATER", "LESS", "IN", "WHERE"}
    
    def _debug_print(self, message: str):
        """Affiche un message seulement en mode debug"""
        if self.debug_mode:
            print(f"[PARSER] {message}")
    
    def parse(self, script: str) -> ASTNode:
        """
        Parse un script GrabLang complet et retourne l'AST
        
        Args:
            script: Le code source à analyser
            
        Returns:
            ASTNode: Racine de l'arbre syntaxique abstrait
        """
        self._debug_print(f"Début du parsing ({len(script)} caractères)")
        
        # Étape 1: Tokenisation
        self.tokens = self._tokenize(script)
        self._debug_print(f"Tokenisation terminée: {len(self.tokens)} tokens")
        
        # Étape 2: Construction de l'AST
        self.current_token_index = 0
        ast = self._parse_program()
        
        self._debug_print("Parsing terminé avec succès")
        return ast
    
    def _tokenize(self, script: str) -> List[Token]:
        """
        Tokenise le script en une liste de tokens
        
        Args:
            script: Le code source à tokeniser
            
        Returns:
            List[Token]: Liste des tokens extraits
        """
        tokens = []
        lines = script.split('\n')
        
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ignore les lignes vides et les commentaires
            if not line or line.startswith('#'):
                continue
            
            # Tokenise cette ligne
            line_tokens = self._tokenize_line(line, line_number)
            tokens.extend(line_tokens)
        
        return tokens
    
    def _tokenize_line(self, line: str, line_number: int) -> List[Token]:
        """
        Tokenise une ligne individuelle
        
        Args:
            line: La ligne à tokeniser
            line_number: Numéro de ligne pour le debugging
            
        Returns:
            List[Token]: Tokens de cette ligne
        """
        tokens = []
        i = 0
        
        while i < len(line):
            # Skip les espaces
            if line[i].isspace():
                i += 1
                continue
            
            # Gestion des accolades
            if line[i] == '{':
                tokens.append(Token(TokenType.BRACE_OPEN, '{', line_number, i))
                i += 1
                continue
            elif line[i] == '}':
                tokens.append(Token(TokenType.BRACE_CLOSE, '}', line_number, i))
                i += 1
                continue
            
            # Gestion des chaînes entre guillemets
            if line[i] in ['"', "'"]:
                quote_char = line[i]
                start_col = i
                i += 1
                value = ""
                
                while i < len(line) and line[i] != quote_char:
                    value += line[i]
                    i += 1
                
                if i < len(line):  # Guillemet fermant trouvé
                    i += 1
                    tokens.append(Token(TokenType.STRING, value, line_number, start_col))
                else:
                    raise SyntaxError(f"Ligne {line_number}: Guillemet non fermé")
                continue
            
            # Gestion des mots/identifiants
            if line[i].isalnum() or line[i] == '_':
                start_col = i
                value = ""
                
                while i < len(line) and (line[i].isalnum() or line[i] in ['_', '-']):
                    value += line[i]
                    i += 1
                
                # Détermine le type de token
                token_type = self._determine_token_type(value, tokens)
                tokens.append(Token(token_type, value, line_number, start_col))
                continue
            
            # Caractère non reconnu
            raise SyntaxError(f"Ligne {line_number}, colonne {i}: Caractère non reconnu '{line[i]}'")
        
        return tokens
    
    def _determine_token_type(self, value: str, existing_tokens: List[Token]) -> TokenType:
        """
        Détermine le type d'un token basé sur sa valeur et son contexte
        
        Args:
            value: La valeur du token
            existing_tokens: Tokens déjà parsés sur cette ligne
            
        Returns:
            TokenType: Le type approprié pour ce token
        """
        upper_value = value.upper()
        
        # Mots-clés de contrôle
        if upper_value in self.control_keywords:
            return TokenType.CONTROL
        
        # Commandes principales
        if upper_value in self.command_keywords:
            return TokenType.COMMAND
        
        # Opérateurs
        if upper_value in self.operators:
            return TokenType.OPERATOR
        
        # Si c'est le premier token d'une ligne, probablement une commande
        if not existing_tokens:
            return TokenType.COMMAND
        
        # Si le token précédent était une commande, c'est probablement une sous-commande
        if existing_tokens and existing_tokens[-1].type == TokenType.COMMAND:
            return TokenType.SUBCOMMAND
        
        # Par défaut, c'est un argument
        return TokenType.ARGUMENT
    
    def _parse_program(self) -> ASTNode:
        """
        Parse le programme complet (point d'entrée principal)
        
        Returns:
            ASTNode: Nœud racine représentant le programme
        """
        program = ASTNode("PROGRAM")
        
        while self.current_token_index < len(self.tokens):
            statement = self._parse_statement()
            if statement:
                program.children.append(statement)
        
        return program
    
    def _parse_statement(self) -> ASTNode:
        """
        Parse une instruction complète
        
        Returns:
            ASTNode: Nœud représentant l'instruction
        """
        if self._is_at_end():
            return None
        
        current_token = self._peek()
        
        # Structure de contrôle
        if current_token.type == TokenType.CONTROL:
            return self._parse_control_structure()
        
        # Commande simple
        elif current_token.type == TokenType.COMMAND:
            return self._parse_command()
        
        else:
            raise SyntaxError(f"Ligne {current_token.line_number}: Instruction attendue, trouvé '{current_token.value}'")
    
    def _parse_control_structure(self) -> ASTNode:
        """
        Parse une structure de contrôle (IF, FOR, WHILE)
        
        Returns:
            ASTNode: Nœud représentant la structure de contrôle
        """
        control_token = self._advance()
        structure_type = control_token.value.upper()
        
        if structure_type == "IF":
            return self._parse_if_statement()
        elif structure_type == "FOR":
            return self._parse_for_statement()
        elif structure_type == "WHILE":
            return self._parse_while_statement()
        else:
            raise SyntaxError(f"Ligne {control_token.line_number}: Structure de contrôle '{structure_type}' non supportée")
    
    def _parse_if_statement(self) -> ASTNode:
        """Parse une structure IF"""
        if_node = ASTNode("IF_STATEMENT", line_number=self._previous().line_number)
        
        # Parse la condition
        condition = self._parse_condition()
        if_node.children.append(condition)
        
        # Parse le bloc
        block = self._parse_block()
        if_node.children.append(block)
        
        return if_node
    
    def _parse_for_statement(self) -> ASTNode:
        """Parse une boucle FOR"""
        for_node = ASTNode("FOR_STATEMENT", line_number=self._previous().line_number)
        
        # Parse la condition FOR (variable IN source)
        condition = self._parse_for_condition()
        for_node.children.append(condition)
        
        # Parse le bloc
        block = self._parse_block()
        for_node.children.append(block)
        
        return for_node
    
    def _parse_while_statement(self) -> ASTNode:
        """Parse une boucle WHILE"""
        while_node = ASTNode("WHILE_STATEMENT", line_number=self._previous().line_number)
        
        # Parse la condition
        condition = self._parse_condition()
        while_node.children.append(condition)
        
        # Parse le bloc
        block = self._parse_block()
        while_node.children.append(block)
        
        return while_node
    
    def _parse_command(self) -> ASTNode:
        """
        Parse une commande simple
        
        Returns:
            ASTNode: Nœud représentant la commande
        """
        command_token = self._advance()
        command_node = ASTNode("COMMAND", command_token.value, line_number=command_token.line_number)
        
        # Parse les arguments de la commande
        while (not self._is_at_end() and 
               self._peek().type not in [TokenType.CONTROL, TokenType.BRACE_OPEN] and
               self._peek().line_number == command_token.line_number):
            
            arg = self._parse_argument()
            command_node.children.append(arg)
        
        return command_node
    
    def _parse_argument(self) -> ASTNode:
        """Parse un argument de commande"""
        token = self._advance()
        
        if token.type == TokenType.STRING:
            return ASTNode("STRING_LITERAL", token.value, line_number=token.line_number)
        elif token.type in [TokenType.SUBCOMMAND, TokenType.ARGUMENT]:
            return ASTNode("IDENTIFIER", token.value, line_number=token.line_number)
        elif token.type == TokenType.OPERATOR:
            # Support des opérateurs comme WHERE, CONTAINS, etc.
            return ASTNode("OPERATOR", token.value, line_number=token.line_number)
        else:
            raise SyntaxError(f"Ligne {token.line_number}: Argument attendu, trouvé '{token.value}'")
    
    def _parse_condition(self) -> ASTNode:
        """Parse une condition logique"""
        condition_node = ASTNode("CONDITION")
        
        # Récupère tous les tokens jusqu'à l'accolade ouvrante ou la fin de ligne
        condition_tokens = []
        start_line = self._peek().line_number if not self._is_at_end() else 0
        
        while (not self._is_at_end() and 
               self._peek().type != TokenType.BRACE_OPEN and
               self._peek().line_number == start_line):
            condition_tokens.append(self._advance())
        
        # Construit la condition comme une chaîne pour l'instant
        condition_text = " ".join(token.value for token in condition_tokens)
        condition_node.value = condition_text
        
        return condition_node
    
    def _parse_for_condition(self) -> ASTNode:
        """Parse une condition de boucle FOR"""
        condition_node = ASTNode("FOR_CONDITION")
        
        # Variable
        if not self._is_at_end():
            var_token = self._advance()
            condition_node.children.append(ASTNode("VARIABLE", var_token.value))
        
        # Mot-clé IN
        if not self._is_at_end() and self._peek().value.upper() == "IN":
            self._advance()  # Consomme IN
        else:
            raise SyntaxError("FOR: Mot-clé 'IN' attendu")
        
        # Source (RANGE ou variable)
        if not self._is_at_end():
            source_token = self._advance()
            
            if source_token.value.upper() == "RANGE":
                # RANGE suivi d'un nombre ou d'une variable
                if not self._is_at_end():
                    range_value = self._advance()
                    range_node = ASTNode("RANGE", range_value.value)
                    condition_node.children.append(range_node)
            else:
                # Variable source
                condition_node.children.append(ASTNode("VARIABLE", source_token.value))
        
        return condition_node
    
    def _parse_block(self) -> ASTNode:
        """Parse un bloc de code entre accolades"""
        if self._is_at_end() or self._peek().type != TokenType.BRACE_OPEN:
            raise SyntaxError("Bloc: Accolade ouvrante '{' attendue")
        
        self._advance()  # Consomme '{'
        
        block_node = ASTNode("BLOCK")
        
        while not self._is_at_end() and self._peek().type != TokenType.BRACE_CLOSE:
            statement = self._parse_statement()
            if statement:
                block_node.children.append(statement)
        
        if self._is_at_end():
            raise SyntaxError("Bloc: Accolade fermante '}' attendue")
        
        self._advance()  # Consomme '}'
        
        return block_node
    
    # Méthodes utilitaires pour la navigation dans les tokens
    
    def _is_at_end(self) -> bool:
        """Vérifie si on a atteint la fin des tokens"""
        return self.current_token_index >= len(self.tokens)
    
    def _peek(self) -> Token:
        """Retourne le token actuel sans l'avancer"""
        if self._is_at_end():
            return None
        return self.tokens[self.current_token_index]
    
    def _previous(self) -> Token:
        """Retourne le token précédent"""
        if self.current_token_index > 0:
            return self.tokens[self.current_token_index - 1]
        return None
    
    def _advance(self) -> Token:
        """Avance au token suivant et retourne le token actuel"""
        if not self._is_at_end():
            self.current_token_index += 1
        return self._previous()
    
    def _check(self, token_type: TokenType) -> bool:
        """Vérifie si le token actuel est du type spécifié"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *token_types: TokenType) -> bool:
        """Vérifie si le token actuel correspond à l'un des types donnés"""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False