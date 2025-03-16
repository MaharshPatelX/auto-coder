#!/usr/bin/env python3
"""
Simplified CLI for the AI Coding System
"""

import os
import sys
import argparse
import time
from pathlib import Path

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_coding_system import run_simplified_coding_system

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Coding System - Generate complete code projects from requirements"
    )
    
    parser.add_argument(
        "prompt", 
        nargs="?", 
        help="Initial project requirements"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=os.path.join(os.getcwd(), "generated_project"),
        help="Output directory for the generated project (defaults to ./generated_project)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start in interactive mode with a questionnaire"
    )
    
    return parser.parse_args()

def interactive_requirements_gathering():
    """Gather project requirements interactively."""
    print("\n🤖 AI Coding System - Interactive Requirements Gathering")
    print("-" * 70)
    
    # Collect basic project information
    project_name = input("\n📋 Project name: ")
    
    print("\n📋 Project type (select number):")
    project_types = [
        "Web application",
        "API / Backend service",
        "CLI tool",
        "Data processing script",
        "Library / Framework",
        "Other (specify)"
    ]
    
    for i, t in enumerate(project_types, 1):
        print(f"  {i}. {t}")
    
    project_type_idx = int(input("\nEnter choice (1-6): ")) - 1
    project_type = project_types[project_type_idx]
    if project_type == "Other (specify)":
        project_type = input("Specify project type: ")
    
    # Language preference
    print("\n📋 Programming language (select number):")
    languages = [
        "Python",
        "JavaScript",
        "TypeScript",
        "Java",
        "C#",
        "Go",
        "Rust",
        "Other (specify)"
    ]
    
    for i, lang in enumerate(languages, 1):
        print(f"  {i}. {lang}")
    
    lang_idx = int(input("\nEnter choice (1-8): ")) - 1
    language = languages[lang_idx]
    if language == "Other (specify)":
        language = input("Specify language: ")
    
    # Functional requirements
    print("\n📋 Functional requirements (what should the system do?):")
    print("  Enter one requirement per line. Press Enter on an empty line when done.")
    
    functional_reqs = []
    while True:
        req = input("  - ")
        if not req:
            break
        functional_reqs.append(req)
    
    # Additional information
    additional_info = input("\n📋 Any additional information or context? ")
    
    # Format everything into a comprehensive prompt
    prompt = f"""
Project: {project_name}
Type: {project_type}
Language: {language}

Functional Requirements:
{chr(10).join('- ' + req for req in functional_reqs)}

Additional Information:
{additional_info}

Based on these requirements, please design and implement a complete, production-ready solution.
"""
    
    print("\n📋 Generated prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    
    confirm = input("\n📋 Do you want to proceed with this prompt? (y/n): ")
    if confirm.lower() != 'y':
        print("Exiting...")
        sys.exit(0)
    
    return prompt

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Use interactive mode if specified or if no prompt is provided
    if args.interactive or not args.prompt:
        prompt = interactive_requirements_gathering()
    # Use provided prompt
    else:
        prompt = args.prompt
    
    # Create output directory
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Print setup information
    print("\n🚀 AI Coding System - Starting")
    print("-" * 70)
    print(f"📁 Output directory: {output_dir}")
    
    # Start the timer
    start_time = time.time()
    
    # Run the coding system
    success = run_simplified_coding_system(prompt, output_dir)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    # Print completion information
    if success:
        print("\n✅ Project generation complete!")
        print("-" * 70)
        print(f"⏱️  Time taken: {int(minutes)} minutes and {int(seconds)} seconds")
        print(f"📁 Project files are available at: {output_dir}")
        print("\nThank you for using the AI Coding System!")
    else:
        print("\n❌ Project generation failed.")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        sys.exit(1)