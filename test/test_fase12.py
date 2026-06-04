# Test suite for PyReact Fase 12: Agent blocks, pipelines, expanded standard library and unified testing.
import unittest
from pyreact.compiler.lexer import Lexer, TT
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase12(unittest.TestCase):
    def test_lexer_agent_pipeline(self):
        code = """
        agent Assistant {
            model = "llama3"
            prompt = "You are a helpful assistant."
            temperature = 0.5
        }
        
        pipeline MasterFlow {
            steps = [Assistant]
        }
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        token_types = [t.type for t in tokens]
        self.assertIn(TT.AGENT, token_types)
        self.assertIn(TT.PIPELINE, token_types)

    def test_parser_agent_pipeline(self):
        code = """
        agent Assistant {
            model = 'llama3'
            prompt = 'You are a helpful assistant.'
            temperature = '0.5'
        }
        
        pipeline MasterFlow {
            steps = [Assistant]
        }
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast_tree = parser.parse()
        
        self.assertEqual(len(ast_tree.agents), 1)
        self.assertEqual(ast_tree.agents[0].name, "Assistant")
        self.assertEqual(ast_tree.agents[0].settings["model"], "llama3")
        
        self.assertEqual(len(ast_tree.pipelines), 1)
        self.assertEqual(ast_tree.pipelines[0].name, "MasterFlow")
        self.assertEqual(ast_tree.pipelines[0].steps, ["Assistant"])

    def test_codegen_agent_pipeline(self):
        code = """
        agent Assistant {
            model = 'llama3'
            prompt = 'You are a helpful assistant.'
            temperature = '0.5'
        }
        
        pipeline MasterFlow {
            steps = [Assistant]
        }
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast_tree = parser.parse()
        
        # Test Flask routes output
        codegen = CodeGenerator(ast_tree, target="flask")
        routes_py = codegen._gen_routes()
        self.assertIn('/api/agent/Assistant', routes_py)
        self.assertIn('/api/pipeline/MasterFlow', routes_py)
        self.assertIn('urllib.request', routes_py)

if __name__ == '__main__':
    unittest.main()
