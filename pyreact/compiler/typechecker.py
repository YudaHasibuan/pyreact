"""PyReact Static Type Checker.

Performs compile-time type validation for:
- Server function parameter types
- State variable types
- Component prop types
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from pyreact.compiler.parser import ProgramNode, FuncDef, ComponentNode


@dataclass
class TypeWarning:
    """Represents a type warning from the type checker."""
    message: str
    line: int = 0
    col: int = 0
    severity: str = "warning"  # warning, error, info
    category: str = "type"     # type, param, state, prop

    def __str__(self):
        prefix = f"[{self.severity.upper()}]"
        location = f" (line {self.line})" if self.line > 0 else ""
        return f"{prefix}{location} {self.message}"


class TypeChecker:
    """Static type checker for PyReact AST."""
    
    # Valid Python types
    PYTHON_TYPES: Set[str] = {
        "str", "int", "float", "bool", "list", "dict", "tuple", "set",
        "None", "NoneType", "any", "Any", "Optional", "Union", "List", "Dict"
    }
    
    # Type compatibility mapping (for inference)
    TYPE_INFERENCES: Dict[str, str] = {
        '""': "str",
        "''": "str",
        '""': "str",
        "0": "int",
        "0.0": "float",
        "False": "bool",
        "True": "bool",
        "[]": "list",
        "{}": "dict",
        "None": "NoneType",
    }
    
    # JavaScript type equivalents for frontend validation
    JS_TYPES: Dict[str, str] = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "None": "null",
        "NoneType": "null",
    }

    def __init__(self):
        self.warnings: List[TypeWarning] = []
        self._function_signatures: Dict[str, FuncDef] = {}

    def check(self, ast: ProgramNode) -> List[TypeWarning]:
        """Run type checking on the AST and return warnings."""
        self.warnings = []
        
        # Build function signature map
        if ast.server and ast.server.functions:
            for func in ast.server.functions:
                self._function_signatures[func.name] = func
        
        # Check server functions
        self._check_server_functions(ast)
        
        # Check components
        self._check_components(ast)
        
        # Check cross-references (server calls from components)
        self._check_server_calls(ast)
        
        return self.warnings

    def _check_server_functions(self, ast: ProgramNode):
        """Validate server function type hints."""
        if not ast.server or not ast.server.functions:
            return
            
        for func in ast.server.functions:
            # Check parameter types
            for param_name, param_type in func.param_types.items():
                if not self._is_valid_type(param_type):
                    self.warnings.append(TypeWarning(
                        message=f"Unknown type '{param_type}' for parameter '{param_name}' in server function '{func.name}'",
                        severity="warning",
                        category="param"
                    ))
            
            # Check return type
            if func.return_type and not self._is_valid_type(func.return_type):
                self.warnings.append(TypeWarning(
                    message=f"Unknown return type '{func.return_type}' for server function '{func.name}'",
                    severity="warning",
                    category="type"
                ))
            
            # Check for missing type hints (info level)
            untyped_params = [p for p in func.params if p not in func.param_types]
            if untyped_params:
                self.warnings.append(TypeWarning(
                    message=f"Parameters {untyped_params} in '{func.name}' have no type hints",
                    severity="info",
                    category="param"
                ))

    def _check_components(self, ast: ProgramNode):
        """Validate component props and state types."""
        for comp in ast.components:
            # Check component name (should be PascalCase)
            if comp.name and not comp.name[0].isupper():
                self.warnings.append(TypeWarning(
                    message=f"Component '{comp.name}' should start with uppercase (PascalCase)",
                    severity="warning",
                    category="prop"
                ))
            
            # Check state variable initializations for type inference
            for state in comp.states:
                inferred_type = self._infer_type(state.initial)
                if inferred_type:
                    # Store inferred type for later validation
                    pass  # Could extend to track type mismatches

    def _check_server_calls(self, ast: ProgramNode):
        """Check that server function calls use correct parameter types."""
        # This would require parsing handler bodies for server.xxx() calls
        # For now, we just validate that called functions exist
        for comp in ast.components:
            for handler in comp.handlers:
                # Simple regex to find server.funcName() calls
                import re
                calls = re.findall(r'server\.(\w+)\s*\(', handler.body)
                for call_name in calls:
                    if call_name not in self._function_signatures:
                        self.warnings.append(TypeWarning(
                            message=f"Call to undefined server function '{call_name}' in handler '{handler.name}'",
                            severity="warning",
                            category="type"
                        ))

    def _is_valid_type(self, type_str: str) -> bool:
        """Check if a type string is valid."""
        # Handle Optional[X], List[X], Dict[K, V] etc.
        base_type = type_str.split("[")[0].strip()
        if base_type in ("Optional", "Union", "List", "Dict", "Tuple", "Set"):
            return True
        return base_type in self.PYTHON_TYPES or base_type[0].isupper()  # Allow custom types

    def _infer_type(self, value: str) -> Optional[str]:
        """Infer type from a literal value."""
        value = value.strip()
        
        # Direct lookup
        if value in self.TYPE_INFERENCES:
            return self.TYPE_INFERENCES[value]
        
        # Number check
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        
        try:
            float(value)
            return "float"
        except ValueError:
            pass
        
        # String check
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return "str"
        
        return None

    def get_js_type(self, python_type: str) -> str:
        """Convert Python type to JavaScript type for frontend validation."""
        base_type = python_type.split("[")[0].strip()
        return self.JS_TYPES.get(base_type, "any")

    def format_warnings(self) -> str:
        """Format all warnings as a readable string."""
        if not self.warnings:
            return ""
        
        lines = ["Type Check Results:"]
        errors = [w for w in self.warnings if w.severity == "error"]
        warnings = [w for w in self.warnings if w.severity == "warning"]
        infos = [w for w in self.warnings if w.severity == "info"]
        
        if errors:
            lines.append(f"  Errors: {len(errors)}")
            for w in errors:
                lines.append(f"    - {w}")
        if warnings:
            lines.append(f"  Warnings: {len(warnings)}")
            for w in warnings:
                lines.append(f"    - {w}")
        if infos:
            lines.append(f"  Info: {len(infos)}")
            for w in infos:
                lines.append(f"    - {w}")
        
        return "\n".join(lines)


def run_type_check(ast: ProgramNode) -> List[TypeWarning]:
    """Convenience function to run type checking on an AST."""
    checker = TypeChecker()
    return checker.check(ast)
