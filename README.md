# AI Coding System

A hierarchical AI agent-based system that automates the entire software development process, from requirements gathering to production-ready code generation.

## 🌟 Features

- **Interactive Requirements Gathering**: Clarifies project needs through targeted questioning
- **Architecture Design**: Creates robust system structures based on requirements
- **Full Code Implementation**: Generates working code across multiple files
- **Automated Testing**: Builds comprehensive test cases and runs them against the implementation
- **Code Quality Checks**: Reviews code for best practices and potential issues
- **Documentation Generation**: Creates README files and code documentation
- **Project Organization**: Sets up proper file structures and organization
- **Multiple Interface Options**: Use via CLI or web interface

## 🧠 Agent Architecture

The system uses a hierarchical team approach with specialized agents:

1. **Project Manager Agent**: Coordinates the entire development process
2. **Requirements Analyst Agent**: Gathers detailed project requirements
3. **Architect Agent**: Designs the system structure and architecture
4. **Developer Agent**: Implements the code based on the architecture
5. **Testing Agent**: Verifies the code through automated tests
6. **Documentation Agent**: Creates comprehensive documentation
7. **Code Review Agent**: Ensures code quality and best practices

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Anthropic API key (for Claude access)
- Tavily API key (for web search capabilities)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-coding-system.git
cd ai-coding-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
MODEL_NAME=deepseek-r1-distill-qwen-32b
GROQ_API_KEY=your_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Usage

#### Command Line Interface

Run in interactive mode:
```bash
python cli/cli.py -i
```

Provide requirements directly:
```bash
python cli/cli.py "Create a Python CLI tool that downloads and analyzes cryptocurrency prices" -o op\crypto_analyzer
```

Use a configuration file:
```bash
python cli/cli.py -c my_project_config.json -o op/my_project
```

#### Web Interface

Launch the Streamlit web app:
```bash
streamlit run web/app.py
```

## 📊 Example Projects

The system can generate a wide variety of projects:

- Web applications
- API/Backend services
- CLI tools
- Data processing scripts
- Libraries/Frameworks
- And more!

## 🔧 System Components

- **LangGraph**: Powers the agent coordination framework
- **deepseek r1 distill qwen 32b**: Provides the reasoning capabilities
- **Python REPL**: Executes and tests generated code
- **File System Access**: Organizes project structure
- **Code Quality Tools**: Ensures adherence to best practices

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) for the agent framework
- [Anthropic](https://www.anthropic.com/) for Claude API
- [Streamlit](https://streamlit.io/) for the web interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.