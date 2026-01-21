#!/usr/bin/env python
"""
CareLedger Test Runner

Run all tests with various configurations
"""
import sys
import subprocess
import argparse


def run_tests(test_type="all", verbose=False, coverage=False):
    """
    Run tests based on specified type
    
    Args:
        test_type: Type of tests to run (all, unit, integration, agents, orchestrator, vector)
        verbose: Enable verbose output
        coverage: Enable coverage reporting
    """
    
    cmd = ["pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Select tests based on type
    if test_type == "all":
        cmd.append("tests/")
    elif test_type == "unit":
        cmd.extend(["-m", "unit", "tests/"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/"])
    elif test_type == "agents":
        cmd.append("tests/test_agents.py")
    elif test_type == "orchestrator":
        cmd.append("tests/test_orchestrator.py")
    elif test_type == "vector":
        cmd.append("tests/test_vector_store.py")
    else:
        print(f"Unknown test type: {test_type}")
        return 1
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    return result.returncode


def run_linting():
    """Run code linting"""
    print("Running flake8 linting...")
    result = subprocess.run([
        "flake8", ".", 
        "--count",
        "--max-line-length=100",
        "--exclude=venv,env,__pycache__,.git"
    ])
    return result.returncode


def run_type_checking():
    """Run type checking with mypy"""
    print("Running mypy type checking...")
    result = subprocess.run([
        "mypy", ".",
        "--ignore-missing-imports",
        "--exclude", "venv|env|tests"
    ])
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="CareLedger Test Runner")
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "agents", "orchestrator", "vector"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Enable coverage reporting"
    )
    
    parser.add_argument(
        "-l", "--lint",
        action="store_true",
        help="Run linting before tests"
    )
    
    parser.add_argument(
        "-t", "--type-check",
        action="store_true",
        help="Run type checking before tests"
    )
    
    args = parser.parse_args()
    
    exit_code = 0
    
    # Run linting if requested
    if args.lint:
        lint_code = run_linting()
        if lint_code != 0:
            print("\n⚠️ Linting failed!")
            exit_code = lint_code
    
    # Run type checking if requested
    if args.type_check:
        type_code = run_type_checking()
        if type_code != 0:
            print("\n⚠️ Type checking failed!")
            exit_code = type_code
    
    # Run tests
    test_code = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    if test_code != 0:
        print("\n❌ Tests failed!")
        exit_code = test_code
    else:
        print("\n✅ All tests passed!")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
