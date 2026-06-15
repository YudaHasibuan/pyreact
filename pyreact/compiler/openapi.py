"""PyReact OpenAPI Schema Generator.

Generates OpenAPI 3.0 specification from server functions with type hints.
"""
from typing import Dict, Any, List, Optional
from pyreact.compiler.parser import ProgramNode, FuncDef


class OpenAPIGenerator:
    """Generates OpenAPI 3.0 specification from PyReact AST."""
    
    # Python type to OpenAPI type mapping
    TYPE_MAP: Dict[str, Dict[str, str]] = {
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "float": {"type": "number", "format": "float"},
        "bool": {"type": "boolean"},
        "list": {"type": "array", "items": {"type": "string"}},
        "dict": {"type": "object"},
        "None": {"type": "null"},
        "NoneType": {"type": "null"},
        "Optional": {"type": "string", "nullable": True},
        "List": {"type": "array"},
        "Dict": {"type": "object"},
    }

    def __init__(self, ast: ProgramNode):
        self.ast = ast
        self.schema: Dict[str, Any] = {}

    def generate(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification."""
        self.schema = {
            "openapi": "3.0.3",
            "info": {
                "title": "PyReact API",
                "description": "Auto-generated API documentation from PyReact server functions",
                "version": "1.0.0",
                "contact": {
                    "name": "PyReact"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5000",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # Generate paths from server functions
        if self.ast.server and self.ast.server.functions:
            for func in self.ast.server.functions:
                self._add_path(func)
        
        # Add default auth endpoints
        self._add_auth_paths()
        
        return self.schema

    def _add_path(self, func: FuncDef):
        """Add a server function as an API path."""
        path = f"/api/{func.name}"
        
        # Build request body schema from parameters
        request_body = self._build_request_body(func)
        
        # Build response schema
        response = self._build_response(func)
        
        # Build the operation
        operation = {
            "summary": func.name.replace("_", " ").title(),
            "description": f"Calls the {func.name} server function",
            "operationId": func.name,
            "tags": ["API"],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": response
                        }
                    }
                },
                "400": {
                    "description": "Bad request - invalid parameters"
                },
                "500": {
                    "description": "Internal server error"
                }
            }
        }
        
        if request_body:
            operation["requestBody"] = request_body
        
        self.schema["paths"][path] = {
            "post": operation
        }

    def _build_request_body(self, func: FuncDef) -> Optional[Dict[str, Any]]:
        """Build request body schema from function parameters."""
        if not func.params:
            return None
        
        properties = {}
        required = []
        
        for param in func.params:
            param_type = func.param_types.get(param, "any")
            schema = self._type_to_schema(param_type)
            properties[param] = schema
            
            # Parameters without default values are required
            # (simplified: all typed params are required)
            if param in func.param_types:
                required.append(param)
        
        if not properties:
            return None
        
        body_schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            body_schema["required"] = required
        
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": body_schema
                }
            }
        }

    def _build_response(self, func: FuncDef) -> Dict[str, Any]:
        """Build response schema."""
        # Default response is an object
        return {
            "type": "object",
            "description": f"Response from {func.name}"
        }

    def _type_to_schema(self, python_type: str) -> Dict[str, Any]:
        """Convert Python type to OpenAPI schema."""
        # Handle Optional[X]
        if python_type.startswith("Optional["):
            inner = python_type[9:-1]
            schema = self._type_to_schema(inner)
            schema["nullable"] = True
            return schema
        
        # Handle List[X]
        if python_type.startswith("List["):
            inner = python_type[5:-1]
            return {
                "type": "array",
                "items": self._type_to_schema(inner)
            }
        
        # Handle Dict[K, V]
        if python_type.startswith("Dict["):
            return {"type": "object"}
        
        # Simple types
        base_type = python_type.split("[")[0].strip()
        if base_type in self.TYPE_MAP:
            return self.TYPE_MAP[base_type].copy()
        
        # Unknown type - default to string
        return {"type": "string", "description": f"Type: {python_type}"}

    def _add_auth_paths(self):
        """Add default authentication endpoints."""
        self.schema["paths"]["/api/login"] = {
            "post": {
                "summary": "User Login",
                "description": "Authenticate user and receive JWT token",
                "operationId": "login",
                "tags": ["Auth"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "token": {"type": "string"},
                                        "user": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Invalid credentials"
                    }
                }
            }
        }
        
        self.schema["paths"]["/api/me"] = {
            "get": {
                "summary": "Get Current User",
                "description": "Get authenticated user information",
                "operationId": "getCurrentUser",
                "tags": ["Auth"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "user": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Not authenticated"
                    }
                }
            }
        }
        
        # Add security scheme
        self.schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }


def generate_openapi(ast: ProgramNode) -> Dict[str, Any]:
    """Convenience function to generate OpenAPI spec from AST."""
    generator = OpenAPIGenerator(ast)
    return generator.generate()


def generate_swagger_html(spec_url: str = "/api/openapi.json") -> str:
    """Generate Swagger UI HTML page."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyReact API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui.css">
    <style>
        body {{ margin: 0; padding: 0; }}
        .swagger-ui .topbar {{ display: none; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({{
            url: "{spec_url}",
            dom_id: "#swagger-ui",
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout"
        }});
    </script>
</body>
</html>'''
