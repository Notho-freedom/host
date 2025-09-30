#!/usr/bin/env python3
"""Script to add @pytest.mark.asyncio decorator to all async test functions."""

import os
import re

def add_asyncio_decorators(file_path):
    """Add @pytest.mark.asyncio decorator to all async test functions in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match async test functions without the decorator
    pattern = r'(\n    )(async def test_\w+\([^)]*\):)'
    
    # Check if pytest.mark.asyncio is already imported and add if not
    if '@pytest.mark.asyncio' not in content:
        # Find all async test functions and add decorator
        def add_decorator(match):
            indent = match.group(1)
            func_def = match.group(2)
            return f'{indent}@pytest.mark.asyncio{indent}{func_def}'
        
        content = re.sub(pattern, add_decorator, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

def main():
    """Process all test files."""
    test_files = [
        'tests/test_api.py',
        'tests/test_integration.py',
        'tests/test_services.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            add_asyncio_decorators(test_file)
        else:
            print(f"File not found: {test_file}")

if __name__ == '__main__':
    main()