# Test suite for PyReact Fase 25: GraphQL API Engine & Type-Safe Queries
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer, TT
from pyreact.compiler.parser import Parser, GraphQLBlock
from pyreact.compiler.codegen import CodeGenerator


SAMPLE_GQL = """
server {
    def get_users():
        return [{"id": 1, "name": "Alice"}]

    def create_user(name: String):
        return {"id": 2, "name": name}
}

graphql {
    type User {
        id: Int!
        name: String!
        email: String
    }

    type Post {
        id: Int!
        title: String!
        author: String
    }

    query users -> get_users
    query user -> get_user

    mutation createUser -> create_user
    mutation deleteUser -> delete_user
}

component App() {
    return (
        <UI.Page>
            <UI.Text>GraphQL App</UI.Text>
        </UI.Page>
    )
}
"""


class TestFase25Lexer(unittest.TestCase):
    def test_graphql_keyword_tokenised(self):
        tokens = Lexer(SAMPLE_GQL).tokenize()
        types = [t.type for t in tokens]
        self.assertIn(TT.GRAPHQL, types, "GRAPHQL token not produced by lexer")

    def test_graphql_block_produces_raw_python(self):
        tokens = Lexer(SAMPLE_GQL).tokenize()
        gql_idx = next(i for i, t in enumerate(tokens) if t.type == TT.GRAPHQL)
        # token after GRAPHQL keyword should be LBRACE then RAW_PYTHON
        sub = [t.type for t in tokens[gql_idx:gql_idx + 4]]
        self.assertIn(TT.LBRACE, sub)
        self.assertIn(TT.RAW_PYTHON, sub)


class TestFase25Parser(unittest.TestCase):
    def _parse(self, src):
        return Parser(Lexer(src).tokenize()).parse()

    def test_graphql_block_parsed(self):
        tree = self._parse(SAMPLE_GQL)
        self.assertIsNotNone(tree.graphql, "graphql block not parsed")
        self.assertIsInstance(tree.graphql, GraphQLBlock)

    def test_types_extracted(self):
        tree = self._parse(SAMPLE_GQL)
        self.assertIn("User", tree.graphql.types)
        self.assertIn("Post", tree.graphql.types)

    def test_type_fields_extracted(self):
        tree = self._parse(SAMPLE_GQL)
        user_fields = tree.graphql.types["User"]
        self.assertIn("id", user_fields)
        self.assertIn("name", user_fields)
        self.assertEqual(user_fields["id"], "Int!")

    def test_queries_extracted(self):
        tree = self._parse(SAMPLE_GQL)
        self.assertIn("users", tree.graphql.queries)
        self.assertEqual(tree.graphql.queries["users"], "get_users")
        self.assertIn("user", tree.graphql.queries)

    def test_mutations_extracted(self):
        tree = self._parse(SAMPLE_GQL)
        self.assertIn("createUser", tree.graphql.mutations)
        self.assertEqual(tree.graphql.mutations["createUser"], "create_user")
        self.assertIn("deleteUser", tree.graphql.mutations)


class TestFase25CodeGen(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_gql_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    def _compile(self, src):
        tokens = Lexer(src).tokenize()
        tree = Parser(tokens).parse()
        cg = CodeGenerator(tree, out_dir=self.out_dir)
        cg.generate()
        return tree

    def test_graphql_schema_py_generated(self):
        self._compile(SAMPLE_GQL)
        schema_path = self.out_dir / "backend" / "graphql_schema.py"
        self.assertTrue(schema_path.exists(), "graphql_schema.py not generated")

    def test_schema_contains_sdl(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "backend" / "graphql_schema.py").read_text(encoding="utf-8")
        self.assertIn("type User", content)
        self.assertIn("type Post", content)
        self.assertIn("type Query", content)
        self.assertIn("type Mutation", content)

    def test_schema_contains_flask_blueprint(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "backend" / "graphql_schema.py").read_text(encoding="utf-8")
        self.assertIn("Blueprint", content)
        self.assertIn("/graphql", content)
        self.assertIn("graphql_bp", content)

    def test_schema_contains_resolver_registry(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "backend" / "graphql_schema.py").read_text(encoding="utf-8")
        self.assertIn("_RESOLVERS", content)
        self.assertIn("get_users", content)
        self.assertIn("create_user", content)

    def test_schema_contains_execute_function(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "backend" / "graphql_schema.py").read_text(encoding="utf-8")
        self.assertIn("_execute", content)

    def test_graphql_client_js_generated(self):
        self._compile(SAMPLE_GQL)
        client_path = self.out_dir / "frontend" / "src" / "graphql_client.js"
        self.assertTrue(client_path.exists(), "graphql_client.js not generated")

    def test_graphql_client_js_has_use_query(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "frontend" / "src" / "graphql_client.js").read_text(encoding="utf-8")
        self.assertIn("useQuery", content)
        self.assertIn("export function useQuery", content)

    def test_graphql_client_js_has_use_mutation(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "frontend" / "src" / "graphql_client.js").read_text(encoding="utf-8")
        self.assertIn("useMutation", content)
        self.assertIn("export function useMutation", content)

    def test_graphql_client_js_has_caching(self):
        self._compile(SAMPLE_GQL)
        content = (self.out_dir / "frontend" / "src" / "graphql_client.js").read_text(encoding="utf-8")
        self.assertIn("_cache", content)
        self.assertIn("cacheKey", content)

    def test_no_graphql_block_skips_generation(self):
        """Without a graphql block, graphql_schema.py should NOT be generated."""
        src = """
        component App() {
            return (<UI.Page><UI.Text>No GQL</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        schema_path = self.out_dir / "backend" / "graphql_schema.py"
        self.assertFalse(schema_path.exists(), "graphql_schema.py should not exist without graphql block")


if __name__ == "__main__":
    unittest.main()
