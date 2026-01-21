# Contributing to CareLedger

Thank you for your interest in contributing to CareLedger! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- Gemini API key

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/careledger.git
cd careledger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run demo to verify setup
python demo.py
```

## 🔧 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes
- Write clean, documented code
- Follow existing code style
- Add docstrings to functions
- Use type hints

### 3. Test Your Changes
```bash
# Run the demo
python demo.py

# Test the UI
streamlit run app.py

# Test the API
python api.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in similarity search"
```

**Commit Message Format:**
```
type(scope): subject

body (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python Code Style
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Docstring Format
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input provided
    """
    pass
```

### Type Hints
Always use type hints:
```python
def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    pass
```

## 🧪 Testing Guidelines

### Adding Tests
Create test files in `tests/` directory:
```python
# tests/test_agents.py
def test_ingestion_agent():
    # Your test here
    pass
```

### Running Tests
```bash
pytest tests/
```

## 📚 Documentation

### Adding Documentation
- Update README.md for user-facing changes
- Add detailed docs in `docs/` for technical changes
- Include examples where helpful

### Documentation Structure
```markdown
## Feature Name

### What It Does
[Brief explanation]

### How to Use
[Code example]

### Why It Matters
[Benefits/use cases]
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional medical record types
- [ ] Enhanced image analysis (MedCLIP integration)
- [ ] Audio transcription (Whisper integration)
- [ ] Unit tests for all agents
- [ ] Performance optimizations

### Medium Priority
- [ ] Additional LLM providers
- [ ] Improved UI/UX
- [ ] Better error messages
- [ ] Localization support

### Documentation
- [ ] More usage examples
- [ ] Video tutorials
- [ ] API documentation improvements
- [ ] Translation to other languages

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues
2. Verify bug in latest version
3. Test with demo data

### Bug Report Template
```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Enter input '...'
3. See error

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.

**Environment:**
- OS: [e.g., Windows 10, macOS 13]
- Python version: [e.g., 3.9.7]
- CareLedger version: [e.g., 1.0.0]

**Additional context**
Any other relevant information.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would this feature work?

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## ⚠️ Important Notes

### Medical Disclaimer
- Never add features that provide medical diagnosis
- Always maintain decision support approach
- Include appropriate disclaimers

### Privacy & Security
- Never commit API keys or sensitive data
- Follow HIPAA best practices
- Patient data must remain isolated

### Code Quality
- All agents must have clear, single responsibilities
- Memory evolution logic must be explicit
- Safety validation required for all outputs

## 🤝 Code Review Process

### What Reviewers Look For
1. Code quality and style
2. Documentation completeness
3. Test coverage
4. Performance impact
5. Security considerations
6. Medical safety compliance

### Getting Your PR Merged
- Address all review comments
- Keep changes focused (one feature per PR)
- Ensure all tests pass
- Update documentation

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email security@careledger.example.com

## 🙏 Thank You

Every contribution helps make CareLedger better for patients and healthcare providers worldwide. Thank you for being part of this mission!

---

**License**: By contributing, you agree that your contributions will be licensed under the MIT License.
