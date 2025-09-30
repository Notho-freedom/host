#!/usr/bin/env python3
"""Check and install missing dependencies."""

import subprocess
import sys
from pathlib import Path

def check_dependency(package):
    """Check if a package is installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main dependency check and installation."""
    
    print("🔍 Checking dependencies...")
    
    # Core dependencies mapping
    dependencies = {
        'fastapi': 'fastapi>=0.104.1',
        'uvicorn': 'uvicorn[standard]>=0.24.0',
        'pydantic': 'pydantic>=2.4.0',
        'edge_tts': 'edge-tts>=6.1.8',
        'langdetect': 'langdetect>=1.0.9',
        'aiohttp': 'aiohttp>=3.9.0',
        'pytest': 'pytest>=7.4.0',
    }
    
    missing_deps = []
    
    for module, package in dependencies.items():
        if check_dependency(module):
            print(f"✅ {module} - installed")
        else:
            print(f"❌ {module} - missing")
            missing_deps.append(package)
    
    if missing_deps:
        print(f"\n📦 Installing {len(missing_deps)} missing dependencies...")
        
        for package in missing_deps:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ Successfully installed {package}")
            else:
                print(f"❌ Failed to install {package}")
        
        print("\n🔄 Re-checking dependencies...")
        
        # Re-check
        all_good = True
        for module in dependencies.keys():
            if not check_dependency(module):
                print(f"❌ {module} - still missing")
                all_good = False
        
        if all_good:
            print("🎉 All dependencies installed successfully!")
        else:
            print("⚠️  Some dependencies are still missing. Please install manually:")
            print("pip install -r requirements.txt")
    else:
        print("\n🎉 All dependencies are already installed!")
    
    # Check optional dependencies
    print("\n🔍 Checking optional dependencies...")
    
    optional_deps = {
        'pygame': 'pygame>=2.5.0  # For audio testing',
        'requests': 'requests>=2.31.0  # For legacy tests'
    }
    
    for module, info in optional_deps.items():
        if check_dependency(module):
            print(f"✅ {module} - installed")
        else:
            print(f"⚠️  {module} - not installed ({info})")

if __name__ == "__main__":
    main()