#!/usr/bin/env python3
"""Migration script to backup old files and setup new structure."""

import shutil
import os
from pathlib import Path
from datetime import datetime

def migrate_old_project():
    """Migrate old project structure to new one."""
    
    backup_dir = Path("backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Files to backup
    old_files = ["app.py", "test.py"]
    
    print("🔄 Starting project migration...")
    
    # Create backup directory
    backup_dir.mkdir(exist_ok=True)
    print(f"📁 Created backup directory: {backup_dir}")
    
    # Backup old files
    for file in old_files:
        if Path(file).exists():
            shutil.copy2(file, backup_dir / file)
            print(f"📋 Backed up: {file}")
    
    # Create .env from example if it doesn't exist
    if not Path(".env").exists() and Path(".env.example").exists():
        shutil.copy2(".env.example", ".env")
        print("⚙️  Created .env from template")
    
    print("\n✅ Migration completed!")
    print(f"📁 Old files backed up in: {backup_dir}")
    print("\n🚀 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure .env file")
    print("3. Run tests: python test_modern.py")
    print("4. Start service: python main.py")

if __name__ == "__main__":
    migrate_old_project()