#!/usr/bin/env python
"""
CareLedger Setup Verification

Verifies that all components are properly installed and configured
"""
import sys
import importlib
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print('='*70)


def check_python_version():
    """Check Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('streamlit', 'Streamlit'),
        ('qdrant_client', 'Qdrant Client'),
        ('google.generativeai', 'Google Generative AI'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('transformers', 'Transformers'),
        ('torch', 'PyTorch'),
        ('PIL', 'Pillow'),
        ('PyPDF2', 'PyPDF2'),
        ('cv2', 'OpenCV'),
        ('dotenv', 'python-dotenv'),
        ('pydantic', 'Pydantic'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas')
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} (NOT INSTALLED)")
            all_installed = False
    
    return all_installed


def check_project_structure():
    """Check if project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_paths = [
        'agents/__init__.py',
        'agents/ingestion_agent.py',
        'agents/memory_agent.py',
        'agents/similarity_agent.py',
        'agents/safety_agent.py',
        'agents/recommendation_agent.py',
        'models/__init__.py',
        'models/schemas.py',
        'utils/__init__.py',
        'utils/embeddings.py',
        'utils/vector_store.py',
        'utils/llm.py',
        'config.py',
        'orchestrator.py',
        'api.py',
        'app.py',
        'demo.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'LICENSE'
    ]
    
    all_exist = True
    for path in required_paths:
        file_path = Path(path)
        if file_path.exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} (MISSING)")
            all_exist = False
    
    return all_exist


def check_imports():
    """Check if core modules can be imported"""
    print("\n🔧 Checking core imports...")
    
    all_imports_ok = True
    
    try:
        from orchestrator import orchestrator
        print("✅ Orchestrator imports OK")
    except Exception as e:
        print(f"❌ Orchestrator imports FAILED: {e}")
        all_imports_ok = False
    
    try:
        from agents.ingestion_agent import ingestion_agent
        print("✅ Ingestion Agent imports OK")
    except Exception as e:
        print(f"❌ Ingestion Agent imports FAILED: {e}")
        all_imports_ok = False
    
    try:
        from utils.vector_store import qdrant_manager
        print("✅ Vector Store imports OK")
    except Exception as e:
        print(f"❌ Vector Store imports FAILED: {e}")
        all_imports_ok = False
    
    try:
        from utils.embeddings import embedding_manager
        print("✅ Embedding Manager imports OK")
    except Exception as e:
        print(f"❌ Embedding Manager imports FAILED: {e}")
        all_imports_ok = False
    
    try:
        from utils.llm import gemini_llm
        print("✅ Gemini LLM imports OK")
    except Exception as e:
        print(f"❌ Gemini LLM imports FAILED: {e}")
        all_imports_ok = False
    
    return all_imports_ok


def check_configuration():
    """Check configuration"""
    print("\n⚙️ Checking configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_example.exists():
        print("✅ .env.example exists")
    else:
        print("❌ .env.example missing")
    
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if GEMINI_API_KEY is set
        with open(env_file) as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and 'your_gemini_api_key' not in content:
                print("✅ GEMINI_API_KEY appears to be configured")
            else:
                print("⚠️ GEMINI_API_KEY not configured (demo will use mock responses)")
    else:
        print("⚠️ .env file not found (create from .env.example)")
    
    return True


def main():
    """Run all verification checks"""
    print_header("CareLedger Setup Verification")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Project Structure", check_project_structure()),
        ("Core Imports", check_imports()),
        ("Configuration", check_configuration())
    ]
    
    print_header("Verification Summary")
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("✅ All checks passed! CareLedger is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Configure GEMINI_API_KEY in .env file")
        print("   2. Run: python demo.py")
        print("   3. Run: streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n📝 Common fixes:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Create .env file: cp .env.example .env")
        print("   • Check Python version: python --version")
        return 1


if __name__ == "__main__":
    sys.exit(main())
