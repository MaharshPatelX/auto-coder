"""
Utility modules for the AI Coding System.

This package contains various utility functions for file handling,
code quality checks, and project management.
"""

from .file_utils import (
    ensure_directory_exists,
    write_text_file,
    read_text_file,
    write_json_file,
    read_json_file,
    write_yaml_file,
    read_yaml_file,
    list_files,
    copy_directory_structure,
    create_zip_archive,
    extract_zip_archive,
    get_project_structure,
    create_project_skeleton,
    find_files_by_content,
    merge_files
)

from .code_quality import (
    format_python_code,
    format_python_file,
    format_python_directory,
    run_pylint,
    run_pylint_directory,
    count_lines_of_code,
    analyze_code_complexity,
    test_python_module,
    check_pep8_compliance,
    generate_docstring,
    add_docstrings_to_file,
    check_for_security_issues,
    optimize_imports
)

__all__ = [
    # File utilities
    'ensure_directory_exists',
    'write_text_file',
    'read_text_file',
    'write_json_file',
    'read_json_file',
    'write_yaml_file',
    'read_yaml_file',
    'list_files',
    'copy_directory_structure',
    'create_zip_archive',
    'extract_zip_archive',
    'get_project_structure',
    'create_project_skeleton',
    'find_files_by_content',
    'merge_files',
    
    # Code quality utilities
    'format_python_code',
    'format_python_file',
    'format_python_directory',
    'run_pylint',
    'run_pylint_directory',
    'count_lines_of_code',
    'analyze_code_complexity',
    'test_python_module',
    'check_pep8_compliance',
    'generate_docstring',
    'add_docstrings_to_file',
    'check_for_security_issues',
    'optimize_imports'
]