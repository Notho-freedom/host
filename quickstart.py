#!/usr/bin/env python3
"""Quick start script for TTS service."""

import subprocess
import sys
import os
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command with description."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_environment():
    """Setup the development environment."""
    print("🚀 Setting up TTS service environment...\n")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ recommended for best compatibility")
    
    steps = [
        ("python check_deps.py", "Checking dependencies"),
        ("python -m pip install --upgrade pip", "Upgrading pip"),
    ]
    
    # Install requirements if file exists
    if Path("requirements.txt").exists():
        steps.append(("pip install -r requirements.txt", "Installing requirements"))
    
    # Setup .env if needed
    if not Path(".env").exists() and Path(".env.example").exists():
        steps.append(("cp .env.example .env" if os.name != 'nt' else "copy .env.example .env", "Creating .env file"))
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            return False
    
    return True

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running tests...")
    
    test_commands = [
        ("python -m pytest tests/ -v", "Running unit tests"),
        ("python test_modern.py --url http://localhost:8000", "Running integration tests"),
    ]
    
    for cmd, desc in test_commands:
        run_command(cmd, desc)

def start_service(dev_mode=True, host="127.0.0.1", port=8000):
    """Start the TTS service."""
    print(f"\n🚀 Starting TTS service on http://{host}:{port}")
    
    if dev_mode:
        cmd = f"python main.py --host {host} --port {port} --reload --debug"
        print("🔧 Development mode - auto-reload enabled")
    else:
        cmd = f"python main.py --host {host} --port {port}"
        print("🏭 Production mode")
    
    print(f"📡 API documentation will be available at: http://{host}:{port}/docs")
    print("🔍 Health check: http://{host}:{port}/health")
    print("\nPress Ctrl+C to stop the service\n")
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")

def main():
    """Main quickstart function."""
    parser = argparse.ArgumentParser(description="TTS Service Quick Start")
    parser.add_argument("--setup", action="store_true", help="Setup environment only")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--prod", action="store_true", help="Production mode (no reload)")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    
    args = parser.parse_args()
    
    # ASCII Art Header
    print("""
    🎙️  TTS Service Quick Start
    ═══════════════════════════
    """)
    
    if args.setup:
        setup_environment()
        return
    
    if args.test:
        run_tests()
        return
    
    # Full startup sequence
    print("Starting complete setup and launch sequence...\n")
    
    # Step 1: Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check errors above.")
        sys.exit(1)
    
    # Step 2: Quick health check
    if Path("main.py").exists():
        print("✅ Main application found")
    else:
        print("❌ main.py not found. Are you in the right directory?")
        sys.exit(1)
    
    # Step 3: Start service
    start_service(
        dev_mode=not args.prod,
        host=args.host,
        port=args.port
    )

if __name__ == "__main__":
    main()