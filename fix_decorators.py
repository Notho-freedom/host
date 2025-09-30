#!/usr/bin/env python3
"""Script to add @pytest.mark.asyncio decorator to all async test functions."""

import re

def fix_test_file(file_path):
    """Add @pytest.mark.asyncio decorator to all async test functions in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for easier processing
    lines = content.split('\n')
    modified_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line defines an async test function
        if re.match(r'\s+async def test_\w+\(.*\):', line):
            # Check if the previous line already has the decorator
            if i > 0 and '@pytest.mark.asyncio' in lines[i-1]:
                # Already has decorator, just add the line
                modified_lines.append(line)
            else:
                # Add decorator before the async def
                indent_match = re.match(r'(\s+)', line)
                indent = indent_match.group(1) if indent_match else '    '
                decorator = f"{indent}@pytest.mark.asyncio"
                modified_lines.append(decorator)
                modified_lines.append(line)
        else:
            modified_lines.append(line)
        
        i += 1
    
    # Join back and write
    new_content = '\n'.join(modified_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")

def main():
    """Process all test files."""
    test_files = [
        'tests/test_api.py',
        'tests/test_integration.py', 
        'tests/test_services.py'
    ]
    
    for test_file in test_files:
        fix_test_file(test_file)

if __name__ == '__main__':
    main()