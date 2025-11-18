#!/usr/bin/env python3
"""
Python 3.13 Compatibility Checker for La Casa de Todos
This script checks if the current Python version and environment
are compatible with the application requirements.
"""
from __future__ import annotations

import sys
import subprocess
import pkg_resources
from typing import List, Tuple, Dict, Any


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.13 or compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:  # Support Python 3.11+
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible"
    else:
        return False, f"✗ Python {version.major}.{version.minor}.{version.micro} is not supported. Please use Python 3.11 or higher."


def check_required_packages() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed with correct versions."""
    required_packages = {
        'Flask': '3.0.3',
        'Werkzeug': '3.0.3',
        'Jinja2': '3.1.4',
        'MarkupSafe': '2.1.5',
        'itsdangerous': '2.2.0',
        'click': '8.1.7',
        'blinker': '1.8.2',
        'requests': '2.32.3',
        'pytz': '2024.1'
    }
    
    results = []
    all_good = True
    
    for package, min_version in required_packages.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version):
                results.append(f"✓ {package} {installed_version} (>= {min_version})")
            else:
                results.append(f"✗ {package} {installed_version} (need >= {min_version})")
                all_good = False
        except pkg_resources.DistributionNotFound:
            results.append(f"✗ {package} not installed (need >= {min_version})")
            all_good = False
    
    return all_good, results


def check_sqlite_version() -> Tuple[bool, str]:
    """Check SQLite version for compatibility."""
    import sqlite3
    version = sqlite3.sqlite_version
    # SQLite 3.35+ is recommended for modern features
    if pkg_resources.parse_version(version) >= pkg_resources.parse_version("3.35.0"):
        return True, f"✓ SQLite {version} is compatible"
    else:
        return False, f"⚠ SQLite {version} may have limited functionality. Consider upgrading to 3.35+"


def run_compatibility_check() -> Dict[str, Any]:
    """Run all compatibility checks."""
    print("🔍 Checking Python 3.13 compatibility for La Casa de Todos...")
    print("=" * 60)
    
    results = {
        'python_ok': False,
        'packages_ok': False,
        'sqlite_ok': False,
        'overall_ok': False
    }
    
    # Check Python version
    python_ok, python_msg = check_python_version()
    results['python_ok'] = python_ok
    print(f"\n📋 Python Version:")
    print(f"   {python_msg}")
    
    # Check packages
    packages_ok, package_results = check_required_packages()
    results['packages_ok'] = packages_ok
    print(f"\n📦 Package Dependencies:")
    for result in package_results:
        print(f"   {result}")
    
    # Check SQLite
    sqlite_ok, sqlite_msg = check_sqlite_version()
    results['sqlite_ok'] = sqlite_ok
    print(f"\n🗃️  Database:")
    print(f"   {sqlite_msg}")
    
    # Overall result
    results['overall_ok'] = python_ok and packages_ok and sqlite_ok
    
    print(f"\n" + "=" * 60)
    if results['overall_ok']:
        print("✅ All compatibility checks passed! Your environment is ready.")
    else:
        print("❌ Some compatibility issues found. Please address them before running the application.")
        
        if not python_ok:
            print("\n🔧 To fix Python version:")
            print("   - Install Python 3.11 or higher")
            print("   - Consider using pyenv or conda to manage Python versions")
        
        if not packages_ok:
            print("\n🔧 To fix package dependencies:")
            print("   pip install -r requirements.txt")
            print("   # Or upgrade specific packages:")
            print("   pip install --upgrade Flask Werkzeug Jinja2")
    
    return results


if __name__ == "__main__":
    try:
        results = run_compatibility_check()
        sys.exit(0 if results['overall_ok'] else 1)
    except Exception as e:
        print(f"❌ Error during compatibility check: {e}")
        sys.exit(1)
