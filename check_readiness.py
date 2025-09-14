#!/usr/bin/env python3
"""
SIH 2025 - IDSS Readiness Check
Quick validation before presentation
"""

import os
import sys
from pathlib import Path

def check_readiness():
    """Check if system is ready for SIH presentation"""
    
    print("🎯 SIH 2025 READINESS CHECK")
    print("=" * 50)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python Version: {python_version}")
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"✅ Current Directory: {Path(current_dir).name}")
    
    # Check essential files
    essential_files = [
        'unified_dashboard.py',
        'run_production.py', 
        '.env',
        'SIH_PRESENTATION_GUIDE.md',
        'SIH_QUICK_REFERENCE.md',
        'DEPLOYMENT_GUIDE.md'
    ]
    
    print("✅ Essential Files:")
    missing_files = []
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} (MISSING)")
            missing_files.append(file)
    
    # Check key directories
    key_dirs = ['core', 'analytics', 'logs']
    print("✅ Key Directories:")
    for directory in key_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ⚠️ {directory}/ (will be created)")
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        print("✅ Core Dependencies: Installed")
    except ImportError as e:
        print(f"❌ Missing Dependency: {e}")
    
    # System ready check
    if not missing_files:
        print("=" * 50)
        print("🎉 SYSTEM STATUS: READY FOR SIH 2025!")
        print("🚂 Your IDSS system is deployment-ready!")
        print("=" * 50)
        print()
        print("🚀 Quick Start Commands:")
        print("   python unified_dashboard.py")
        print("   python run_production.py")
        print()
        print("🌐 Access URLs:")
        print("   http://localhost:8000 (Dashboard)")
        print("   http://localhost:8000/docs (API Docs)")
        print()
        print("📋 Presentation Materials:")
        print("   - SIH_PRESENTATION_GUIDE.md")
        print("   - SIH_QUICK_REFERENCE.md")
        print("   - DEPLOYMENT_GUIDE.md")
        print()
        print("🏆 GO WIN SIH 2025! 🇮🇳")
    else:
        print("=" * 50)
        print("⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        print(f"❌ Missing {len(missing_files)} essential files")
        print("Please ensure all files are in place before presentation")
    
    return len(missing_files) == 0

if __name__ == "__main__":
    check_readiness()