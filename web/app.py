import streamlit as st
import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
import threading
from typing import Dict, Any, List, Optional

# Add parent directory to path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_coding_system import run_coding_system

# Initialize session state for tracking progress
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'current_phase' not in st.session_state:
    st.session_state.current_phase = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'output_dir' not in st.session_state:
    st.session_state.output_dir = None
if 'files' not in st.session_state:
    st.session_state.files = []
if 'download_ready' not in st.session_state:
    st.session_state.download_ready = False

def gather_project_requirements() -> Dict[str, Any]:
    """Gather project requirements through a Streamlit form."""
    
    st.header("📋 Project Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name", "my_awesome_project")
        
        project_type = st.selectbox(
            "Project Type",
            [
                "Web application",
                "API / Backend service",
                "CLI tool",
                "Data processing script",
                "Library / Framework",
                "Other"
            ]
        )
        
        if project_type == "Other":
            project_type = st.text_input("Specify Project Type")
    
    with col2:
        language = st.selectbox(
            "Programming Language",
            [
                "Python",
                "JavaScript",
                "TypeScript",
                "Java",
                "C#",
                "Go",
                "Rust",
                "Other"
            ]
        )
        
        if language == "Other":
            language = st.text_input("Specify Programming Language")
            
        frameworks = st.text_input("Frameworks/Libraries (comma-separated)")
    
    st.subheader("Functional Requirements")
    st.write("What should the system do? List specific features.")
    
    functional_reqs = []
    for i in range(5):
        req = st.text_input(f"Requirement {i+1}", key=f"func_req_{i}")
        if req:
            functional_reqs.append(req)
    
    st.subheader("Non-functional Requirements")
    st.write("Performance, security, usability, etc.")
    
    nonfunctional_reqs = []
    for i in range(3):
        req = st.text_input(f"Requirement {i+1}", key=f"nonfunc_req_{i}")
        if req:
            nonfunctional_reqs.append(req)
    
    additional_info = st.text_area("Additional Information or Context", height=100)
    
    # Format everything into a comprehensive prompt
    prompt = f"""
Project: {project_name}
Type: {project_type}
Language: {language}
Frameworks/Libraries: {frameworks}

Functional Requirements:
{chr(10).join('- ' + req for req in functional_reqs)}

Non-functional Requirements:
{chr(10).join('- ' + req for req in nonfunctional_reqs)}

Additional Information:
{additional_info}

Based on these requirements, please design and implement a complete, production-ready solution.
"""
    
    # Create config dictionary
    config = {
        "project_name": project_name,
        "project_type": project_type,
        "language": language,
        "frameworks": frameworks,
        "functional_requirements": functional_reqs,
        "non_functional_requirements": nonfunctional_reqs,
        "additional_info": additional_info,
        "prompt": prompt,
    }
    
    return config

def create_project_in_thread(prompt: str, output_dir: str):
    """Run the coding system in a separate thread to prevent Streamlit from freezing."""
    try:
        # Reset progress
        st.session_state.progress = 0
        st.session_state.current_phase = "starting"
        st.session_state.messages = []
        st.session_state.is_running = True
        st.session_state.download_ready = False
        
        # Create a monitor function to track progress
        def progress_monitor():
            phases = [
                "requirements_gathering",
                "architecture_design",
                "implementation",
                "testing",
                "documentation",
                "review_and_finalization"
            ]
            
            while st.session_state.is_running:
                # Update progress based on current phase
                if st.session_state.current_phase in phases:
                    phase_idx = phases.index(st.session_state.current_phase)
                    progress = (phase_idx / len(phases)) * 100
                    st.session_state.progress = int(progress)
                
                time.sleep(0.5)
        
        # Start the monitor in a separate thread
        monitor_thread = threading.Thread(target=progress_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run the coding system
        project_dir = run_coding_system(prompt, output_dir)
        
        # Update session state with project directory
        st.session_state.output_dir = output_dir
        
        # Gather file list
        files = []
        for root, _, filenames in os.walk(output_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, output_dir)
                files.append(rel_path)
        
        st.session_state.files = files
        st.session_state.progress = 100
        st.session_state.current_phase = "complete"
        st.session_state.download_ready = True
        
    except Exception as e:
        st.session_state.messages.append(f"❌ Error: {str(e)}")
    finally:
        st.session_state.is_running = False

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Coding System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Coding System")
    st.write("Generate complete, production-ready code projects from requirements")
    
    # Sidebar - Configuration
    st.sidebar.header("⚙️ Configuration")
    
    # API keys
    api_key = st.sidebar.text_input("Groq API Key", type="password")
    tavily_key = st.sidebar.text_input("Tavily API Key (for search)", type="password")
    
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    
    # Model selection
    model = st.sidebar.selectbox(
        "Model",
        [
            "qwen-qwq-32b",
            "mistral-saba-24b",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
        ]
    )
    
    if model:
        os.environ["MODEL_NAME"] = model
    
    # Output directory
    output_path = st.sidebar.text_input(
        "Output Directory", 
        os.path.join(os.getcwd(), "generated_project")
    )
    
    # Manual prompt option
    use_manual_prompt = st.sidebar.checkbox("Use Manual Prompt")
    
    # Main form for project specification
    if use_manual_prompt:
        st.header("📝 Project Prompt")
        prompt = st.text_area("Enter your detailed project requirements", height=300)
        config = {"prompt": prompt}
    else:
        config = gather_project_requirements()
        
        # Preview prompt
        st.header("📝 Generated Prompt")
        st.code(config["prompt"], language="text")
    
    # Save/load configuration
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Configuration"):
            config_str = json.dumps(config, indent=2)
            st.download_button(
                "Download Configuration File",
                config_str,
                file_name=f"{config.get('project_name', 'project')}_config.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("Load Configuration", type=["json"])
        if uploaded_file is not None:
            config = json.load(uploaded_file)
            st.experimental_rerun()
    
    # Start generation
    if st.button("🚀 Generate Project", disabled=st.session_state.is_running):
        # Create an output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Start the generation in a separate thread
        thread = threading.Thread(
            target=create_project_in_thread,
            args=(config["prompt"], output_path)
        )
        thread.daemon = True
        thread.start()
    
    # Progress display
    if st.session_state.is_running or st.session_state.progress > 0:
        st.header("⏳ Generation Progress")
        
        # Progress bar
        st.progress(st.session_state.progress / 100)
        
        # Phase indicator
        phase_display = st.session_state.current_phase.replace("_", " ").title()
        st.write(f"Current phase: **{phase_display}**")
        
        # Placeholder for logs
        log_container = st.container()
        
        with log_container:
            for msg in st.session_state.messages:
                st.write(msg)
    
    # Results display when complete
    if st.session_state.download_ready:
        st.header("✅ Project Generated!")
        st.write(f"Project files are available at: `{st.session_state.output_dir}`")
        
        # File tree display
        st.subheader("📁 Project Files")
        
        for file in st.session_state.files:
            st.write(f"- `{file}`")
        
        # Prepare zip file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            shutil.make_archive(
                tmp_file.name[:-4],  # Remove .zip extension for make_archive
                'zip',
                st.session_state.output_dir
            )
            
            with open(tmp_file.name, 'rb') as f:
                st.download_button(
                    "📦 Download Project as ZIP",
                    f,
                    file_name=f"{os.path.basename(st.session_state.output_dir)}.zip",
                    mime="application/zip"
                )

if __name__ == "__main__":
    main()