"""
Tests unitaires pour GrabLang
"""

import unittest
import sys
from pathlib import Path

# Ajoute le répertoire parent au PYTHONPATH pour pouvoir importer grablang
sys.path.insert(0, str(Path(__file__).parent.parent))

from grablang.core.interpreter import GrabInterpreter


class TestGrabInterpreter(unittest.TestCase):
    """Tests pour l'interpréteur principal"""
    
    def setUp(self):
        """Initialise un interpréteur pour chaque test"""
        self.interpreter = GrabInterpreter(debug_mode=False)
    
    def test_interpreter_initialization(self):
        """Test que l'interpréteur s'initialise correctement"""
        self.assertIsInstance(self.interpreter, GrabInterpreter)
        self.assertIsInstance(self.interpreter.variables, dict)
        self.assertIsInstance(self.interpreter.commands, dict)
    
    def test_variable_management(self):
        """Test la gestion des variables"""
        # Test set_variable
        self.interpreter.set_variable("test_var", "test_value")
        self.assertEqual(self.interpreter.get_variable("test_var"), "test_value")
        
        # Test variable inexistante
        self.assertIsNone(self.interpreter.get_variable("nonexistent"))
    
    def test_parse_line(self):
        """Test le parsing des lignes de commande"""
        # Test parsing simple
        tokens = self.interpreter._parse_line('LOAD URL "https://example.com"')
        expected = ['LOAD', 'URL', '"https://example.com"']
        self.assertEqual(tokens, expected)
        
        # Test parsing avec guillemets simples
        tokens = self.interpreter._parse_line("GET ATTR 'href'")
        expected = ['GET', 'ATTR', "'href'"]
        self.assertEqual(tokens, expected)
        
        # Test parsing sans guillemets
        tokens = self.interpreter._parse_line("SELECT ALL div")
        expected = ['SELECT', 'ALL', 'div']
        self.assertEqual(tokens, expected)
    
    def test_evaluate_condition(self):
        """Test l'évaluation des conditions"""
        # Prépare des variables de test
        self.interpreter.set_variable("test_list", [1, 2, 3])
        self.interpreter.set_variable("empty_list", [])
        self.interpreter.set_variable("test_string", "hello world")
        
        # Test EXISTS
        self.assertTrue(self.interpreter._evaluate_condition("test_list EXISTS"))
        self.assertFalse(self.interpreter._evaluate_condition("nonexistent EXISTS"))
        
        # Test NOT EXISTS
        self.assertFalse(self.interpreter._evaluate_condition("test_list NOT EXISTS"))
        self.assertTrue(self.interpreter._evaluate_condition("nonexistent NOT EXISTS"))
        
        # Test EMPTY
        self.assertTrue(self.interpreter._evaluate_condition("empty_list EMPTY"))
        self.assertFalse(self.interpreter._evaluate_condition("test_list EMPTY"))
        
        # Test NOT EMPTY
        self.assertFalse(self.interpreter._evaluate_condition("empty_list NOT EMPTY"))
        self.assertTrue(self.interpreter._evaluate_condition("test_list NOT EMPTY"))
        
        # Test CONTAINS
        self.assertTrue(self.interpreter._evaluate_condition("test_string CONTAINS world"))
        self.assertFalse(self.interpreter._evaluate_condition("test_string CONTAINS xyz"))


class TestCommandLoading(unittest.TestCase):
    """Tests pour le chargement des commandes"""
    
    def setUp(self):
        """Initialise un interpréteur pour chaque test"""
        self.interpreter = GrabInterpreter(debug_mode=False)
    
    def test_commands_loaded(self):
        """Test que les commandes sont chargées"""
        # Vérifie que certaines commandes de base sont présentes
        expected_commands = ['LOAD', 'SELECT', 'FILTER', 'GET', 'PRINT', 'SAVE', 'USE']
        
        for command in expected_commands:
            with self.subTest(command=command):
                self.assertIn(command, self.interpreter.commands, 
                            f"Commande {command} non trouvée")


if __name__ == '__main__':
    # Lance les tests
    unittest.main(verbosity=2)