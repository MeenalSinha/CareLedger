#!/usr/bin/env python3
"""
CareLedger Compatibility Verification Script
Checks that all files work together correctly
"""
import sys
import os
import ast

print("="*70)
print("CARELEDGER COMPATIBILITY VERIFICATION")
print("="*70)

# Check 1: Python syntax
print("\n1. Checking Python Syntax...")
files_to_check = [
    'config.py',
    'models/schemas.py',
    'utils/embeddings.py',
    'utils/vector_store.py',
    'utils/llm.py',
    'agents/ingestion_agent.py',
    'agents/memory_agent.py',
    'agents/similarity_agent.py',
    'agents/safety_agent.py',
    'agents/recommendation_agent.py',
    'orchestrator.py',
    'app.py',
    'api.py',
    'demo.py',
    'demo_memory_evolution.py',
    'verify_setup.py',
    'run_tests.py'
]

syntax_ok = True
for filepath in files_to_check:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                ast.parse(f.read())
            print(f"  ✓ {filepath}")
        except SyntaxError as e:
            print(f"  ✗ {filepath}: Syntax error at line {e.lineno}")
            syntax_ok = False
    else:
        print(f"  ⚠ {filepath}: Not found")

# Check 2: Import structure
print("\n2. Checking Import Structure...")

required_exports = {
    'config.py': ['settings'],
    'models/schemas.py': ['RecordType', 'Modality', 'MedicalRecord', 'PatientQuery', 
                          'SimilarCase', 'RetrievalResult', 'IngestionRequest',
                          'TimelineEvent', 'PatientTimeline'],
    'utils/embeddings.py': ['embedding_manager', 'EmbeddingManager'],
    'utils/vector_store.py': ['qdrant_manager', 'QdrantManager'],
    'utils/llm.py': ['gemini_llm', 'GeminiLLM'],
    'agents/ingestion_agent.py': ['ingestion_agent', 'IngestionAgent'],
    'agents/memory_agent.py': ['memory_agent', 'PatientMemoryAgent'],
    'agents/similarity_agent.py': ['similarity_agent', 'SimilarityReasoningAgent'],
    'agents/safety_agent.py': ['safety_agent', 'SafetyEthicsAgent'],
    'agents/recommendation_agent.py': ['recommendation_agent', 'RecommendationAgent'],
    'orchestrator.py': ['orchestrator', 'CareLedgerOrchestrator'],
}

import_ok = True
for filepath, required in required_exports.items():
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            missing = []
            for item in required:
                # Check for class definitions or variable assignments
                if f"class {item}" not in content and f"{item} =" not in content:
                    missing.append(item)
            
            if missing:
                print(f"  ✗ {filepath}: Missing exports: {', '.join(missing)}")
                import_ok = False
            else:
                print(f"  ✓ {filepath}")

# Check 3: Cross-file dependencies
print("\n3. Checking Cross-File Dependencies...")

dependencies = {
    'orchestrator.py': [
        'from agents.ingestion_agent import ingestion_agent',
        'from agents.memory_agent import memory_agent',
        'from agents.similarity_agent import similarity_agent',
        'from agents.safety_agent import safety_agent',
        'from agents.recommendation_agent import recommendation_agent',
        'from models.schemas import',
        'from utils.vector_store import qdrant_manager',
        'from utils.llm import gemini_llm',
    ],
    'app.py': [
        'from orchestrator import orchestrator',
        'from models.schemas import',
    ],
    'api.py': [
        'from orchestrator import orchestrator',
        'from models.schemas import',
    ],
    'demo.py': [
        'from orchestrator import orchestrator',
        'from models.schemas import',
    ],
}

deps_ok = True
for filepath, expected_imports in dependencies.items():
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            missing = []
            for imp in expected_imports:
                if imp not in content:
                    missing.append(imp)
            
            if missing:
                print(f"  ✗ {filepath}: Missing imports")
                for m in missing:
                    print(f"      {m}")
                deps_ok = False
            else:
                print(f"  ✓ {filepath}")

# Check 4: File structure
print("\n4. Checking File Structure...")

required_structure = {
    'agents/__init__.py': True,
    'models/__init__.py': True,
    'utils/__init__.py': True,
    'tests/__init__.py': True,
    'data/uploads/.gitkeep': True,
    '.env.example': True,
    '.gitignore': True,
    'requirements.txt': True,
    'README.md': True,
    'LICENSE': True,
}

structure_ok = True
for filepath, required in required_structure.items():
    if os.path.exists(filepath):
        print(f"  ✓ {filepath}")
    else:
        print(f"  ✗ {filepath}: Missing")
        structure_ok = False

# Check 5: Pydantic model compatibility
print("\n5. Checking Pydantic Model Compatibility...")

# Check RetrievalResult has all required fields
if os.path.exists('models/schemas.py'):
    with open('models/schemas.py', 'r') as f:
        content = f.read()
        
        required_fields = [
            'evidence_trace',
            'reasoning_steps',
            'evidence_summary'
        ]
        
        model_ok = True
        for field in required_fields:
            if field not in content or 'RetrievalResult' not in content:
                print(f"  ✗ RetrievalResult missing field: {field}")
                model_ok = False
        
        if model_ok:
            print("  ✓ RetrievalResult has all required fields")

# Final summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

all_ok = syntax_ok and import_ok and deps_ok and structure_ok

if all_ok:
    print("✅ All compatibility checks passed!")
    print("\n🎉 CareLedger is ready to run!")
    print("\nNext steps:")
    print("  1. pip install -r requirements.txt")
    print("  2. cp .env.example .env")
    print("  3. Add GEMINI_API_KEY to .env")
    print("  4. python demo.py")
    print("  5. streamlit run app.py")
else:
    print("❌ Some compatibility issues found")
    print("\nPlease fix the issues above before running")

print("="*70)

sys.exit(0 if all_ok else 1)
