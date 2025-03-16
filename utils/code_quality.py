"""
Code quality utilities for the AI Coding System.
These utilities help with code formatting, linting, and analysis.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Tuple
import black
import re
import ast
import io
from importlib.util import spec_from_file_location, module_from_spec

# Try to import pylint-related modules, with fallbacks
try:
    from pylint.lint import Run
    from pylint.reporters.text import TextReporter
    PYLINT_AVAILABLE = True
except ImportError:
    PYLINT_AVAILABLE = False


def format_python_code(code: str, line_length: int = 88) -> str:
    """
    Format Python code using Black.
    
    Args:
        code: Python code to format
        line_length: Maximum line length
        
    Returns:
        Formatted code
    """
    try:
        mode = black.Mode(
            line_length=line_length,
            string_normalization=True,
            is_pyi=False,
        )
        return black.format_str(code, mode=mode)
    except Exception as e:
        print(f"Black formatting error: {str(e)}")
        return code


def format_python_file(file_path: Union[str, Path], line_length: int = 88) -> bool:
    """
    Format a Python file using Black.
    
    Args:
        file_path: Path to the Python file
        line_length: Maximum line length
        
    Returns:
        True if formatting was successful, False otherwise
    """
    path = Path(file_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        formatted_code = format_python_code(code, line_length)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(formatted_code)
            
        return True
    except Exception as e:
        print(f"Error formatting {path}: {str(e)}")
        return False


def format_python_directory(directory_path: Union[str, Path], 
                           line_length: int = 88,
                           recursive: bool = True) -> Dict[str, bool]:
    """
    Format all Python files in a directory.
    
    Args:
        directory_path: Path to the directory
        line_length: Maximum line length
        recursive: Whether to search recursively
        
    Returns:
        Dictionary mapping file paths to formatting success
    """
    path = Path(directory_path)
    
    if recursive:
        py_files = list(path.glob("**/*.py"))
    else:
        py_files = list(path.glob("*.py"))
    
    results = {}
    for py_file in py_files:
        results[str(py_file)] = format_python_file(py_file, line_length)
    
    return results


def run_pylint(file_path: Union[str, Path]) -> Tuple[str, float]:
    """
    Run Pylint on a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (report text, score)
    """
    if not PYLINT_AVAILABLE:
        return "Pylint not available", 0.0
    
    path = Path(file_path)
    
    output = io.StringIO()
    reporter = TextReporter(output)
    
    # Run pylint with a custom reporter to capture output
    try:
        Run(
            [str(path)],
            reporter=reporter,
            exit=False
        )
        
        # Extract score from report
        report = output.getvalue()
        score_match = re.search(r"Your code has been rated at ([-\d.]+)/10", report)
        score = float(score_match.group(1)) if score_match else 0.0
        
        return report, score
    except Exception as e:
        return f"Error running Pylint: {str(e)}", 0.0


def run_pylint_directory(directory_path: Union[str, Path],
                        recursive: bool = True) -> Dict[str, Tuple[str, float]]:
    """
    Run Pylint on all Python files in a directory.
    
    Args:
        directory_path: Path to the directory
        recursive: Whether to search recursively
        
    Returns:
        Dictionary mapping file paths to (report, score) tuples
    """
    path = Path(directory_path)
    
    if recursive:
        py_files = list(path.glob("**/*.py"))
    else:
        py_files = list(path.glob("*.py"))
    
    results = {}
    for py_file in py_files:
        results[str(py_file)] = run_pylint(py_file)
    
    return results


def count_lines_of_code(file_path: Union[str, Path]) -> Dict[str, int]:
    """
    Count lines of code, comments, and blank lines in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary with counts
    """
    path = Path(file_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = total_lines - blank_lines - comment_lines
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'comment_ratio': comment_lines / code_lines if code_lines > 0 else 0
        }
    except Exception as e:
        print(f"Error counting lines in {path}: {str(e)}")
        return {
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'comment_ratio': 0
        }


def analyze_code_complexity(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Analyze code complexity metrics for a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary with complexity metrics
    """
    path = Path(file_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Count different types of nodes
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        import_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
        
        # Count complexity metrics
        class NodeCounter(ast.NodeVisitor):
            def __init__(self):
                self.loop_count = 0
                self.if_count = 0
                self.try_count = 0
                
            def visit_For(self, node):
                self.loop_count += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.loop_count += 1
                self.generic_visit(node)
                
            def visit_If(self, node):
                self.if_count += 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                self.try_count += 1
                self.generic_visit(node)
        
        counter = NodeCounter()
        counter.visit(tree)
        
        # Calculate lines of code
        loc = count_lines_of_code(path)
        
        # Calculate cyclomatic complexity (very simplified)
        # For a more accurate measure, a proper tool like radon would be better
        cyclomatic_complexity = counter.if_count + counter.loop_count + counter.try_count + 1
        
        return {
            'classes': class_count,
            'functions': function_count,
            'imports': import_count,
            'loops': counter.loop_count,
            'conditionals': counter.if_count,
            'try_blocks': counter.try_count,
            'lines_of_code': loc,
            'cyclomatic_complexity': cyclomatic_complexity
        }
    except Exception as e:
        print(f"Error analyzing complexity of {path}: {str(e)}")
        return {
            'classes': 0,
            'functions': 0,
            'imports': 0,
            'loops': 0,
            'conditionals': 0,
            'try_blocks': 0,
            'lines_of_code': count_lines_of_code(path),
            'cyclomatic_complexity': 0
        }


def test_python_module(file_path: Union[str, Path],
                      function_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Import and test a Python module.
    
    Args:
        file_path: Path to the Python file
        function_name: Optional function to call after import
        
    Returns:
        Tuple of (success, message)
    """
    path = Path(file_path)
    
    try:
        # Create a module spec
        module_name = path.stem
        spec = spec_from_file_location(module_name, path)
        
        if spec is None:
            return False, f"Could not create spec for {path}"
        
        # Create the module
        module = module_from_spec(spec)
        
        # Execute the module
        spec.loader.exec_module(module)
        
        # Call a function if specified
        if function_name:
            if not hasattr(module, function_name):
                return False, f"Function {function_name} not found in {path}"
            
            # Call the function
            try:
                func = getattr(module, function_name)
                result = func()
                return True, f"Function {function_name} executed successfully: {result}"
            except Exception as e:
                return False, f"Error calling {function_name}: {str(e)}"
        
        return True, f"Module {module_name} imported successfully"
    except Exception as e:
        return False, f"Error importing {path}: {str(e)}"


def check_pep8_compliance(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Check PEP 8 compliance of a Python file using pycodestyle.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (compliant, violations)
    """
    path = Path(file_path)
    
    try:
        # Run pycodestyle as a subprocess
        result = subprocess.run(
            ["pycodestyle", str(path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, []
        else:
            violations = [line for line in result.stdout.split('\n') if line]
            return False, violations
    except FileNotFoundError:
        return False, ["pycodestyle not installed or not in PATH"]
    except Exception as e:
        return False, [f"Error checking PEP 8 compliance: {str(e)}"]


def generate_docstring(function_code: str) -> str:
    """
    Generate a docstring for a Python function.
    
    Args:
        function_code: Python function code
        
    Returns:
        Generated docstring
    """
    try:
        # Parse the function code
        tree = ast.parse(function_code)
        
        # Find the function definition
        function_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_def = node
                break
        
        if not function_def:
            return "Cannot generate docstring: No function definition found"
        
        # Get function name
        function_name = function_def.name
        
        # Get parameters
        params = []
        for arg in function_def.args.args:
            if arg.arg != 'self':
                params.append(arg.arg)
        
        # Check for return statements
        returns = False
        for node in ast.walk(function_def):
            if isinstance(node, ast.Return) and node.value is not None:
                returns = True
                break
        
        # Generate docstring
        docstring = f'"""\n{function_name}'
        if params or returns:
            docstring += '\n\n'
        
        # Add parameter descriptions
        for param in params:
            docstring += f'    Args:\n        {param}: Description of {param}\n'
        
        # Add return description
        if returns:
            if params:
                docstring += '\n'
            docstring += '    Returns:\n        Description of return value\n'
        
        docstring += '    """'
        
        return docstring
    except Exception as e:
        return f'"""\nError generating docstring: {str(e)}\n"""'


def add_docstrings_to_file(file_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Add docstrings to all functions and classes in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (success, modified_code)
    """
    path = Path(file_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse the code
        tree = ast.parse(code)
        
        # Track modifications
        modifications = []
        
        # Find all function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Skip if already has a docstring
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    continue
                
                # Get the code for this node
                node_code = ast.get_source_segment(code, node)
                
                if node_code:
                    # Generate docstring
                    if isinstance(node, ast.FunctionDef):
                        docstring = generate_docstring(node_code)
                    else:  # ClassDef
                        docstring = f'"""\n{node.name} class.\n\nDescription of the class\n"""'
                    
                    # Insert docstring after the first line
                    lines = node_code.split('\n')
                    modified_code = lines[0] + '\n    ' + docstring + '\n' + '\n'.join(lines[1:])
                    
                    # Add to modifications list
                    modifications.append((node_code, modified_code))
        
        # Apply modifications in reverse order to maintain positions
        modified_code = code
        for original, replacement in reversed(modifications):
            modified_code = modified_code.replace(original, replacement)
        
        return True, modified_code
    except Exception as e:
        return False, f"Error adding docstrings: {str(e)}"


def check_for_security_issues(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Check for common security issues in Python code.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of security issues found
    """
    path = Path(file_path)
    
    # Common security patterns to check
    patterns = [
        {
            'pattern': r'eval\s*\(',
            'description': 'Use of eval() can be dangerous if input is not sanitized',
            'severity': 'high'
        },
        {
            'pattern': r'exec\s*\(',
            'description': 'Use of exec() can be dangerous if input is not sanitized',
            'severity': 'high'
        },
        {
            'pattern': r'pickle\.loads',
            'description': 'Unpickling data can lead to remote code execution',
            'severity': 'high'
        },
        {
            'pattern': r'shell\s*=\s*True',
            'description': 'Running shell commands with shell=True can be vulnerable to injection',
            'severity': 'medium'
        },
        {
            'pattern': r'\.format\(.*?__.*?\)',
            'description': 'String formatting with object attributes can lead to information disclosure',
            'severity': 'medium'
        },
        {
            'pattern': r'os\.system\(',
            'description': 'Using os.system() can be vulnerable to command injection',
            'severity': 'medium'
        },
        {
            'pattern': r'subprocess\.call\([^,]*?,\s*shell=True',
            'description': 'Using subprocess with shell=True can be vulnerable to command injection',
            'severity': 'medium'
        },
        {
            'pattern': r'request\.get\([^)]*?verify\s*=\s*False',
            'description': 'Disabling SSL verification is insecure',
            'severity': 'medium'
        },
        {
            'pattern': r'input\(',
            'description': 'Using raw input() can be dangerous if not properly validated',
            'severity': 'low'
        },
        {
            'pattern': r'DEBUG\s*=\s*True',
            'description': 'Debug mode enabled in production code',
            'severity': 'low'
        }
    ]
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        issues = []
        for pattern_info in patterns:
            pattern = pattern_info['pattern']
            matches = re.finditer(pattern, code)
            
            for match in matches:
                # Get line number
                line_number = code[:match.start()].count('\n') + 1
                
                # Get the line content
                lines = code.split('\n')
                line_content = lines[line_number - 1] if line_number <= len(lines) else ''
                
                issues.append({
                    'line': line_number,
                    'content': line_content,
                    'description': pattern_info['description'],
                    'severity': pattern_info['severity']
                })
        
        return issues
    except Exception as e:
        print(f"Error checking security issues in {path}: {str(e)}")
        return []


def optimize_imports(file_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Optimize and organize imports in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (success, modified_code)
    """
    path = Path(file_path)
    
    try:
        # Run isort as a subprocess
        result = subprocess.run(
            ["isort", "--profile", "black", str(path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # Read the modified file
            with open(path, 'r', encoding='utf-8') as f:
                modified_code = f.read()
            
            return True, modified_code
        else:
            return False, f"Error optimizing imports: {result.stderr}"
    except FileNotFoundError:
        return False, "isort not installed or not in PATH"
    except Exception as e:
        return False, f"Error optimizing imports: {str(e)}"