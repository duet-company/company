#!/usr/bin/env python3
"""
Test Validation Script for Duet Company Backend

Validates the testing framework implementation and checks for any issues.
This script addresses Issue #35: Testing and validation.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def check_test_structure():
    """Check if test structure is complete."""
    print("🔍 Checking test structure...")
    
    test_dir = Path("tests")
    required_files = [
        "conftest.py",
        "conftest_extended.py", 
        "test_chat_api.py",
        "test_schema.py",
        "test_query.py",
        "agents/test_query_agent.py",
        "agents/test_agent_framework.py",
        "integration/test_api_integration.py",
        "integration/test_e2e_workflows.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (test_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    else:
        print("✅ All required test files present")
        return True

def check_test_markers():
    """Check if test markers are properly defined."""
    print("\n🔍 Checking test markers...")
    
    try:
        with open("tests/conftest_extended.py", "r") as f:
            content = f.read()
            
        required_markers = [
            "unit", "integration", "e2e", "security", 
            "performance", "load", "slow"
        ]
        
        missing_markers = []
        for marker in required_markers:
            if f'\"markers\", \"{marker}: marks tests as' not in content:
                missing_markers.append(marker)
        
        if missing_markers:
            print(f"❌ Missing markers: {missing_markers}")
            return False
        else:
            print("✅ All test markers defined")
            return True
            
    except Exception as e:
        print(f"❌ Error checking markers: {e}")
        return False

def check_workflow_config():
    """Check GitHub Actions workflow configuration."""
    print("\n🔍 Checking GitHub Actions workflow...")
    
    workflow_path = Path(".github/workflows/backend-tests.yml")
    if not workflow_path.exists():
        print("❌ GitHub Actions workflow not found")
        return False
    
    try:
        with open(workflow_path, "r") as f:
            content = f.read()
            
        required_jobs = ["test"]
        required_steps = [
            "Checkout code",
            "Set up Python",
            "Install dependencies",
            "Run unit tests",
            "Run integration tests",
            "Run e2e tests",
            "Generate coverage report"
        ]
        
        # Check for required jobs
        if "jobs:" not in content or "test:" not in content:
            print("❌ Missing test job in workflow")
            return False
        
        # Check for required steps
        missing_steps = []
        for step in required_steps:
            if step not in content:
                missing_steps.append(step)
        
        if missing_steps:
            print(f"❌ Missing workflow steps: {missing_steps}")
            return False
        else:
            print("✅ GitHub Actions workflow properly configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking workflow: {e}")
        return False

def check_dependencies():
    """Check if test dependencies are properly defined."""
    print("\n🔍 Checking test dependencies...")
    
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open(requirements_path, "r") as f:
            content = f.read()
        
        required_packages = [
            "pytest", "pytest-cov", "pytest-asyncio", 
            "pytest-xdist", "httpx"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing dependencies: {missing_packages}")
            return False
        else:
            print("✅ All test dependencies present")
            return True
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_test_scripts():
    """Check if test scripts are present."""
    print("\n🔍 Checking test scripts...")
    
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        script_files = list(scripts_dir.glob("*.py"))
        if script_files:
            print(f"✅ Found {len(script_files)} test scripts in scripts directory")
            return True
    
    # Check for test report generator
    report_gen = Path("tests/test_report_generator.py")
    if report_gen.exists():
        print("✅ Test report generator found")
        return True
    else:
        print("❌ No test scripts found")
        return False

def simulate_test_run():
    """Simulate test run to check configuration."""
    print("\n🔍 Simulating test configuration check...")
    
    try:
        # Try to import test modules
        sys.path.insert(0, ".")
        
        # Check if test modules can be imported
        test_modules = [
            "tests.conftest",
            "tests.conftest_extended",
            "tests.test_chat_api",
            "tests.agents.test_query_agent",
            "tests.integration.test_api_integration"
        ]
        
        failed_imports = []
        for module in test_modules:
            try:
                __import__(module)
            except ImportError as e:
                failed_imports.append((module, str(e)))
        
        if failed_imports:
            print("❌ Failed to import test modules:")
            for module, error in failed_imports:
                print(f"   {module}: {error}")
            return False
        else:
            print("✅ All test modules can be imported")
            return True
            
    except Exception as e:
        print(f"❌ Error during test simulation: {e}")
        return False

def generate_validation_report():
    """Generate validation report."""
    print("\n📊 Generating validation report...")
    
    # Run all checks
    checks = {
        "Test Structure": check_test_structure(),
        "Test Markers": check_test_markers(),
        "Workflow Config": check_workflow_config(),
        "Dependencies": check_dependencies(),
        "Test Scripts": check_test_scripts(),
        "Test Simulation": simulate_test_run()
    }
    
    # Calculate summary
    total_checks = len(checks)
    passed_checks = sum(checks.values())
    failed_checks = total_checks - passed_checks
    
    # Generate report
    report = {
        "validation_timestamp": time.time(),
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "success_rate": (passed_checks / total_checks) * 100 if total_checks > 0 else 0,
        "checks": checks,
        "recommendations": []
    }
    
    # Generate recommendations
    if not checks["Test Structure"]:
        report["recommendations"].append("Add missing test files to ensure complete test coverage")
    
    if not checks["Test Markers"]:
        report["recommendations"].append("Update conftest_extended.py to include all required markers")
    
    if not checks["Workflow Config"]:
        report["recommendations"].append("Fix GitHub Actions workflow configuration")
    
    if not checks["Dependencies"]:
        report["recommendations"].append("Add missing test dependencies to requirements.txt")
    
    if not checks["Test Scripts"]:
        report["recommendations"].append("Create test scripts for automated testing")
    
    if not checks["Test Simulation"]:
        report["recommendations"].append("Fix import issues in test modules")
    
    # Save report
    report_path = Path("test-validation-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"💾 Validation report saved to: {report_path}")
    
    # Print summary
    print(f"\n📋 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed_checks}/{total_checks}")
    print(f"❌ Failed: {failed_checks}/{total_checks}")
    print(f"📈 Success Rate: {report['success_rate']:.1f}%")
    
    if report["recommendations"]:
        print(f"\n📝 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    return report

if __name__ == "__main__":
    print("🚀 Starting Test Validation for Duet Company Backend")
    print("=" * 60)
    
    report = generate_validation_report()
    
    if report["success_rate"] >= 80:
        print(f"\n🎉 Test validation PASSED ({report['success_rate']:.1f}%)")
        sys.exit(0)
    else:
        print(f"\n⚠️ Test validation FAILED ({report['success_rate']:.1f}%)")
        sys.exit(1)