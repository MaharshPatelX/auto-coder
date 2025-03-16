"""
File utility functions for the AI Coding System.
These utilities help with file operations and project structure management.
"""

import os
import shutil
import json
import yaml
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object of the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text_file(file_path: Union[str, Path], content: str, ensure_dir: bool = True) -> Path:
    """
    Write content to a text file, optionally creating parent directories.
    
    Args:
        file_path: Path to the file
        content: Text content to write
        ensure_dir: Create parent directories if they don't exist
        
    Returns:
        Path object of the written file
    """
    path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(path.parent)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return path


def read_text_file(file_path: Union[str, Path]) -> str:
    """
    Read text content from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Text content of the file
    
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_json_file(file_path: Union[str, Path], data: Any, ensure_dir: bool = True, indent: int = 2) -> Path:
    """
    Write data to a JSON file, optionally creating parent directories.
    
    Args:
        file_path: Path to the file
        data: Data to write as JSON
        ensure_dir: Create parent directories if they don't exist
        indent: JSON indentation level
        
    Returns:
        Path object of the written file
    """
    path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(path.parent)
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)
        
    return path


def read_json_file(file_path: Union[str, Path]) -> Any:
    """
    Read data from a JSON file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Parsed JSON data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_yaml_file(file_path: Union[str, Path], data: Any, ensure_dir: bool = True) -> Path:
    """
    Write data to a YAML file, optionally creating parent directories.
    
    Args:
        file_path: Path to the file
        data: Data to write as YAML
        ensure_dir: Create parent directories if they don't exist
        
    Returns:
        Path object of the written file
    """
    path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(path.parent)
        
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False)
        
    return path


def read_yaml_file(file_path: Union[str, Path]) -> Any:
    """
    Read data from a YAML file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Parsed YAML data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
    """
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def list_files(directory_path: Union[str, Path], 
               pattern: str = "*", 
               recursive: bool = False) -> List[Path]:
    """
    List files in a directory, optionally matching a pattern and recursively.
    
    Args:
        directory_path: Path to the directory
        pattern: Glob pattern to match files
        recursive: Whether to search recursively
        
    Returns:
        List of Path objects for matched files
    """
    path = Path(directory_path)
    
    if recursive:
        return list(path.glob(f"**/{pattern}"))
    else:
        return list(path.glob(pattern))


def copy_directory_structure(source_dir: Union[str, Path], 
                             target_dir: Union[str, Path],
                             ignore_patterns: Optional[List[str]] = None) -> None:
    """
    Copy a directory structure from source to target.
    
    Args:
        source_dir: Source directory path
        target_dir: Target directory path
        ignore_patterns: List of patterns to ignore
        
    Returns:
        None
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    ensure_directory_exists(target_path)
    
    ignore = None
    if ignore_patterns:
        ignore = shutil.ignore_patterns(*ignore_patterns)
    
    shutil.copytree(source_path, target_path, dirs_exist_ok=True, ignore=ignore)


def create_zip_archive(source_dir: Union[str, Path], 
                       zip_file_path: Union[str, Path],
                       ignore_patterns: Optional[List[str]] = None) -> Path:
    """
    Create a ZIP archive from a directory.
    
    Args:
        source_dir: Source directory path
        zip_file_path: Path for the ZIP file
        ignore_patterns: List of patterns to ignore
        
    Returns:
        Path object of the created ZIP file
    """
    source_path = Path(source_dir)
    zip_path = Path(zip_file_path)
    
    ensure_directory_exists(zip_path.parent)
    
    # Convert ignore patterns to a function
    def should_include(file_path):
        if not ignore_patterns:
            return True
        
        rel_path = os.path.relpath(file_path, source_path)
        for pattern in ignore_patterns:
            import fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return False
        return True
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_path):
            for file in files:
                file_path = os.path.join(root, file)
                if should_include(file_path):
                    arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)
    
    return zip_path


def extract_zip_archive(zip_file_path: Union[str, Path], 
                       target_dir: Union[str, Path]) -> Path:
    """
    Extract a ZIP archive to a directory.
    
    Args:
        zip_file_path: Path to the ZIP file
        target_dir: Target directory for extraction
        
    Returns:
        Path object of the extraction directory
    """
    zip_path = Path(zip_file_path)
    target_path = Path(target_dir)
    
    ensure_directory_exists(target_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(target_path)
    
    return target_path


def get_project_structure(directory_path: Union[str, Path], 
                         max_depth: int = None) -> Dict[str, Any]:
    """
    Generate a dictionary representing the directory structure.
    
    Args:
        directory_path: Path to the directory
        max_depth: Maximum depth to traverse
        
    Returns:
        Dictionary representing the directory structure
    """
    path = Path(directory_path)
    
    def _get_structure(current_path, current_depth=0):
        if max_depth is not None and current_depth > max_depth:
            return "..."
        
        result = {}
        
        try:
            for item in current_path.iterdir():
                if item.is_dir():
                    result[item.name] = _get_structure(item, current_depth + 1)
                else:
                    result[item.name] = None  # Files are leaf nodes
        except PermissionError:
            return "Permission denied"
        
        return result
    
    return {path.name: _get_structure(path)}


def create_project_skeleton(project_dir: Union[str, Path], 
                           structure: Dict[str, Any]) -> Path:
    """
    Create a project directory structure from a dictionary skeleton.
    
    Args:
        project_dir: Project directory path
        structure: Dictionary representing the directory structure
        
    Returns:
        Path object of the project directory
    """
    project_path = Path(project_dir)
    
    def _create_structure(current_path, structure_dict):
        for name, contents in structure_dict.items():
            path = current_path / name
            
            if contents is None:
                # This is a file
                path.touch()
            else:
                # This is a directory
                path.mkdir(parents=True, exist_ok=True)
                if isinstance(contents, dict):
                    _create_structure(path, contents)
    
    # Get the root name and contents
    root_name, root_contents = next(iter(structure.items()))
    
    # Create the root directory
    root_path = project_path / root_name
    root_path.mkdir(parents=True, exist_ok=True)
    
    # Create the structure
    if isinstance(root_contents, dict):
        _create_structure(root_path, root_contents)
    
    return project_path


def find_files_by_content(directory_path: Union[str, Path], 
                         search_text: str,
                         file_pattern: str = "*",
                         recursive: bool = True) -> List[Path]:
    """
    Find files containing specific text.
    
    Args:
        directory_path: Path to the directory
        search_text: Text to search for
        file_pattern: Pattern to match files
        recursive: Whether to search recursively
        
    Returns:
        List of Path objects for files containing the search text
    """
    matching_files = []
    
    for file_path in list_files(directory_path, file_pattern, recursive):
        try:
            content = read_text_file(file_path)
            if search_text in content:
                matching_files.append(file_path)
        except (UnicodeDecodeError, IsADirectoryError):
            # Skip binary files and directories
            pass
    
    return matching_files


def merge_files(file_paths: List[Union[str, Path]], 
               output_path: Union[str, Path],
               separator: str = "\n\n") -> Path:
    """
    Merge multiple text files into a single file.
    
    Args:
        file_paths: List of file paths to merge
        output_path: Path for the output file
        separator: Separator to use between files
        
    Returns:
        Path object of the merged file
    """
    paths = [Path(p) for p in file_paths]
    output = Path(output_path)
    
    contents = []
    for path in paths:
        try:
            content = read_text_file(path)
            contents.append(content)
        except Exception as e:
            contents.append(f"Error reading {path}: {str(e)}")
    
    return write_text_file(output, separator.join(contents))