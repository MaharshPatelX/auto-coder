"""
Simplified AI Coding System - Single agent version
This version uses a single agent for simplicity and reliability
"""


def safe_write_file(file_path, content):
    """Safely write content to a file, handling encoding issues"""
    try:
        # Try to write with UTF-8 encoding (preferred)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except UnicodeEncodeError:
        # Fallback to ASCII with replacement if UTF-8 fails
        try:
            sanitized_content = sanitize_text(content)
            with open(file_path, "w", encoding="ascii", errors="replace") as f:
                f.write(sanitized_content)
            print(f"Warning: Saved file {file_path} with ASCII encoding (some characters replaced)")
        except Exception as e:
            raise Exception(f"Failed to write file {file_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to write file {file_path}: {str(e)}")


def sanitize_text(text):
    """
    Sanitize text to remove problematic characters for Windows file system.
    """
    # Replace problematic characters with their ASCII equivalents or remove them
    replacements = {
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '—': '-',
        '–': '-',
        '…': '...',
        '•': '*',
        # Add more replacements as needed
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Additional fallback - encode to ASCII and back, replacing problematic chars
    try:
        text = text.encode('ascii', 'replace').decode('ascii')
    except:
        # If that fails, go character by character
        cleaned = []
        for char in text:
            try:
                char.encode('ascii')
                cleaned.append(char)
            except:
                cleaned.append('?')
        text = ''.join(cleaned)
    
    return text

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

# Langchain imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def create_coding_agent():
    """Create the LLM-based coding agent"""
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    # Get model name, default to qwen-qwq-32b
    model_name = os.getenv("MODEL_NAME")
    
    # Initialize the LLM
    return ChatGroq(
        model=model_name,
        temperature=0.4,
        max_tokens=40000,
        api_key=api_key
    )

def create_project_structure(output_dir: str):
    """Create the basic project directory structure"""
    os.makedirs(output_dir, exist_ok=True)
    
    directories = [
        "src",
        "tests",
        "docs",
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(output_dir, directory), exist_ok=True)
    
    return output_dir

def generate_requirements_document(llm, prompt: str, output_dir: str):
    """Generate the requirements document based on the initial prompt"""
    system_prompt = """
    You are a requirements analyst. Your task is to create a detailed requirements document for the following project.
    Make sure to cover:
    1. Functional requirements
    2. Non-functional requirements
    3. User stories
    4. Technical constraints
    
    Format your response as Markdown.
    Use only ASCII characters in your response - no special quotes, dashes, or unicode symbols.
    """
    
    # Get requirements
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    
    # Sanitize content before saving
    content = sanitize_text(response.content)
    
    # Save requirements
    requirements_dir = os.path.join(output_dir, "docs")
    os.makedirs(requirements_dir, exist_ok=True)
    
    file_path = os.path.join(requirements_dir, "requirements.md")
    safe_write_file(file_path, content)
    
    print("✅ Generated requirements document")
    return content

def generate_architecture_design(llm, requirements: str, output_dir: str):
    """Generate architecture design document"""
    system_prompt = """
    You are a software architect. Based on the following requirements, create a detailed architecture design document.
    Include:
    1. High-level architecture
    2. Component diagram
    3. Data models
    4. API definitions (if applicable)
    5. File structure
    
    Format your response as Markdown.
    Use only ASCII characters in your response - no special quotes, dashes, or unicode symbols.
    """
    
    # Get architecture design
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Requirements:\n\n{requirements}")
    ])
    
    # Sanitize content before saving
    content = sanitize_text(response.content)
    
    # Save architecture design
    design_dir = os.path.join(output_dir, "docs")
    os.makedirs(design_dir, exist_ok=True)
    
    file_path = os.path.join(design_dir, "architecture.md")
    safe_write_file(file_path, content)
    
    print("✅ Generated architecture design")
    return content

def generate_code_files(llm, requirements: str, architecture: str, output_dir: str):
    """Generate code files based on requirements and architecture"""
    system_prompt = """
    You are a software developer. Based on the provided requirements and architecture, implement the necessary code files.
    First, list all the files you'll create with their paths.
    Then, for each file, provide the complete content.
    
    Format your response with clear separators between files, for example:
    
    FILE: src/main.py
    ```python
    # Code content here
    ```
    
    FILE: src/utils.py
    ```python
    # Code content here
    ```
    
    Make sure each file is complete and functional.
    Use only ASCII characters in your code - no special quotes, dashes, or unicode symbols.
    """
    
    # Get code implementation
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Requirements:\n\n{requirements}\n\nArchitecture:\n\n{architecture}")
    ])
    
    # Parse and save code files
    content = sanitize_text(response.content)
    file_sections = content.split("FILE: ")
    
    created_files = []
    
    for section in file_sections[1:]:  # Skip the first empty section
        lines = section.strip().split("\n")
        file_path = lines[0].strip()
        
        # Extract code content
        code_start = section.find("```")
        code_end = section.rfind("```")
        
        if code_start != -1 and code_end != -1 and code_end > code_start:
            # Extract content between the first and last code block markers
            code_content = section[code_start:code_end].strip()
            
            # Remove the code block markers
            code_content = code_content.replace("```python", "").replace("```", "").strip()
            
            # Save the file
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            safe_write_file(full_path, code_content)
            
            created_files.append(file_path)
            print(f"✅ Generated file: {file_path}")
    
    print(f"✅ Created {len(created_files)} code files")
    return created_files

def generate_tests(llm, requirements: str, created_files: List[str], output_dir: str):
    """Generate test files for the created code"""
    # Read the content of created files to inform test generation
    files_content = {}
    for file_path in created_files:
        full_path = os.path.join(output_dir, file_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                files_content[file_path] = f.read()
        except UnicodeDecodeError:
            try:
                with open(full_path, "r", encoding="ascii", errors="replace") as f:
                    files_content[file_path] = f.read()
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {str(e)}")
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {str(e)}")
    
    files_content_str = "\n\n".join([f"FILE: {path}\n```python\n{content}\n```" for path, content in files_content.items()])
    
    system_prompt = """
    You are a software tester. Based on the requirements and code implementation, create appropriate test files.
    Make sure to test all critical functionality.
    
    Format your response with clear separators between files, for example:
    
    FILE: tests/test_main.py
    ```python
    # Test code here
    ```
    
    FILE: tests/test_utils.py
    ```python
    # Test code here
    ```
    
    Make sure each test file is complete and follows testing best practices.
    Use only ASCII characters in your code - no special quotes, dashes, or unicode symbols.
    """
    
    # Get test implementation
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Requirements:\n\n{requirements}\n\nImplementation:\n\n{files_content_str}")
    ])
    
    # Parse and save test files
    content = sanitize_text(response.content)
    file_sections = content.split("FILE: ")
    
    created_tests = []
    
    for section in file_sections[1:]:  # Skip the first empty section
        lines = section.strip().split("\n")
        file_path = lines[0].strip()
        
        # Extract code content
        code_start = section.find("```")
        code_end = section.rfind("```")
        
        if code_start != -1 and code_end != -1 and code_end > code_start:
            # Extract content between the first and last code block markers
            code_content = section[code_start:code_end].strip()
            
            # Remove the code block markers
            code_content = code_content.replace("```python", "").replace("```", "").strip()
            
            # Save the file
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            safe_write_file(full_path, code_content)
            
            created_tests.append(file_path)
            print(f"✅ Generated test file: {file_path}")
    
    print(f"✅ Created {len(created_tests)} test files")
    return created_tests

def generate_documentation(llm, requirements: str, architecture: str, created_files: List[str], output_dir: str):
    """Generate project documentation including README"""
    files_summary = "\n".join(created_files)
    
    system_prompt = """
    You are a technical writer. Create comprehensive documentation for the project.
    Create a README.md file for the project root, and any additional documentation needed.
    
    For the README.md, include:
    1. Project name and description
    2. Installation instructions
    3. Usage examples
    4. Features
    5. Dependencies
    6. Configuration
    
    Format your response with clear separators between files, for example:
    
    FILE: README.md
    ```markdown
    # Project Name
    
    Description...
    ```
    
    FILE: docs/usage_guide.md
    ```markdown
    # Usage Guide
    
    Details...
    ```
    
    Make sure documentation is clear, concise, and helpful for users.
    Use only ASCII characters in your documentation - no special quotes, dashes, or unicode symbols.
    """
    
    # Get documentation
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Requirements:\n\n{requirements}\n\nArchitecture:\n\n{architecture}\n\nProject files:\n{files_summary}")
    ])
    
    # Parse and save documentation files
    content = sanitize_text(response.content)
    file_sections = content.split("FILE: ")
    
    created_docs = []
    
    for section in file_sections[1:]:  # Skip the first empty section
        lines = section.strip().split("\n")
        file_path = lines[0].strip()
        
        # Extract content
        content_start = section.find("```")
        content_end = section.rfind("```")
        
        if content_start != -1 and content_end != -1 and content_end > content_start:
            # Extract content between the first and last code block markers
            doc_content = section[content_start:content_end].strip()
            
            # Remove the code block markers
            doc_content = doc_content.replace("```markdown", "").replace("```", "").strip()
            
            # Save the file
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            safe_write_file(full_path, doc_content)
            
            created_docs.append(file_path)
            print(f"✅ Generated documentation file: {file_path}")
    
    print(f"✅ Created {len(created_docs)} documentation files")
    return created_docs

def run_simplified_coding_system(prompt: str, output_dir: str):
    """Run the simplified coding system end-to-end"""
    print("\n🚀 Starting Simplified AI Coding System")
    print("-" * 70)
    
    try:
        # Create the agent
        llm = create_coding_agent()
        
        # Create project structure
        create_project_structure(output_dir)
        
        # Phase 1: Requirements
        print("\n📋 PHASE 1: Requirements Analysis")
        requirements = generate_requirements_document(llm, prompt, output_dir)
        
        # Phase 2: Architecture
        print("\n🏗️ PHASE 2: Architecture Design")
        architecture = generate_architecture_design(llm, requirements, output_dir)
        
        # Phase 3: Implementation
        print("\n💻 PHASE 3: Code Implementation")
        created_files = generate_code_files(llm, requirements, architecture, output_dir)
        
        # Phase 4: Testing
        print("\n🧪 PHASE 4: Test Creation")
        created_tests = generate_tests(llm, requirements, created_files, output_dir)
        
        # Phase 5: Documentation
        print("\n📚 PHASE 5: Documentation")
        created_docs = generate_documentation(llm, requirements, architecture, created_files, output_dir)
        
        print("\n✅ Project generation complete!")
        print(f"📁 Project files are available at: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simplified_coding_system.py \"<project requirements>\" <output_directory>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output_dir = sys.argv[2]
    
    success = run_simplified_coding_system(prompt, output_dir)
    sys.exit(0 if success else 1)