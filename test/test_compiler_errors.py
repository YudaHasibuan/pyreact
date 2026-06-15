import unittest
from pyreact.compiler.errors import validate_source_integrity
from pyreact.compiler.lexer import Lexer, LexerError
from pyreact.compiler.parser import Parser, ParseError

class TestCompilerErrors(unittest.TestCase):
    def test_validate_source_integrity(self):
        # 1. useState
        with self.assertRaises(ParseError) as ctx:
            validate_source_integrity("component Home():\n    name, setName = useState('')")
        self.assertIn("use_state()", ctx.exception.suggestion)
        
        # 2. class=
        with self.assertRaises(ParseError) as ctx:
            validate_source_integrity("<div class='flex'>")
        self.assertIn("className=", ctx.exception.suggestion)
        
        # 3. export default
        with self.assertRaises(ParseError) as ctx:
            validate_source_integrity("export default component Home():")
        self.assertIn("tidak perlu di-export secara manual", ctx.exception.suggestion)
        
        # 4. Capitalized block keyword
        with self.assertRaises(ParseError) as ctx:
            validate_source_integrity("Server { }")
        self.assertIn("huruf kecil", ctx.exception.suggestion)
        
        # 5. JS Comments
        with self.assertRaises(ParseError) as ctx:
            validate_source_integrity("  // This is comment")
        self.assertIn("gunakan `#` bukan `//` untuk komentar", ctx.exception.suggestion)

    def test_lexer_errors(self):
        # 1. Unclosed string literal
        with self.assertRaises(LexerError) as ctx:
            Lexer('name = "unclosed').tokenize()
        self.assertIn("String literal tidak ditutup", str(ctx.exception))
        
        # 2. Unknown top level character
        with self.assertRaises(LexerError) as ctx:
            Lexer('$').tokenize()
        self.assertIn("Karakter tidak dikenal di tingkat atas", str(ctx.exception))

    def test_parser_errors(self):
        # 1. SyntaxError in server block
        code_server_err = """
        server {
            def hello()
                return "hello"
        }
        """
        with self.assertRaises(ParseError) as ctx:
            Parser(Lexer(code_server_err).tokenize()).parse()
        self.assertIn("Kesalahan sintaksis Python di block server", str(ctx.exception))
        
        # 2. SyntaxError in realtime block
        code_realtime_err = """
        realtime {
            provider = "socket.io"
            def on_connect()
                pass
        }
        """
        with self.assertRaises(ParseError) as ctx:
            Parser(Lexer(code_realtime_err).tokenize()).parse()
        self.assertIn("Kesalahan sintaksis Python di block realtime", str(ctx.exception))
        
        # 3. SyntaxError in middleware block
        code_mw_err = """
        middleware {
            def auth(request)
                pass
        }
        """
        with self.assertRaises(ParseError) as ctx:
            Parser(Lexer(code_mw_err).tokenize()).parse()
        self.assertIn("Kesalahan sintaksis Python di block middleware", str(ctx.exception))
        
        # 4. Unexpected top-level token
        code_toplevel_err = """
        x = 5
        """
        with self.assertRaises(ParseError) as ctx:
            Parser(Lexer(code_toplevel_err).tokenize()).parse()
        self.assertIn("Token tingkat atas tidak valid", str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
