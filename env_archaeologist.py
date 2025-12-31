#!/usr/bin/env python3
"""
ENV Variable Archaeologist - Digging through code like Indiana Jones through ancient ruins.
Finds environment variables so you don't have to ask "What does this do?" for the 100th time.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Regex to find env var patterns - because developers love to hide them everywhere
ENV_PATTERNS = [
    r'os\.getenv\(["\']([^"\']+)["\']\)',  # os.getenv('VAR')
    r'os\.environ\[?["\']([^"\']+)["\']\]?',  # os.environ['VAR'] or os.environ.get('VAR')
    r'\$\{?([A-Z_][A-Z0-9_]*)\}?',  # ${VAR} or $VAR (bash style)
    r'process\.env\.([A-Z_][A-Z0-9_]*)',  # process.env.VAR (Node.js refugees)
]

def find_env_vars_in_file(filepath):
    """Scans a file like a detective looking for clues at a crime scene."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return set()
    
    found_vars = set()
    for pattern in ENV_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        found_vars.update(matches)
    return found_vars

def main():
    """Main function - where the magic (and mild disappointment) happens."""
    if len(sys.argv) < 2:
        print("Usage: python env_archaeologist.py <directory>")
        print("Example: python env_archaeologist.py .")
        sys.exit(1)
    
    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Directory '{target_dir}' not found. Did you check under the couch?")
        sys.exit(1)
    
    # Skip these directories - they're like the boring parts of museums
    skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'env'}
    
    env_vars_by_file = defaultdict(list)
    all_env_vars = set()
    
    # Walk through files like you're exploring ancient ruins
    for filepath in target_dir.rglob('*'):
        if filepath.is_file() and not any(skip in str(filepath) for skip in skip_dirs):
            if filepath.suffix in {'.py', '.js', '.ts', '.sh', '.env', '.yml', '.yaml'}:
                found = find_env_vars_in_file(filepath)
                if found:
                    env_vars_by_file[str(filepath.relative_to(target_dir))] = sorted(found)
                    all_env_vars.update(found)
    
    # Print results like you're presenting evidence in court
    print(f"\n🔍 Found {len(all_env_vars)} unique environment variables in {len(env_vars_by_file)} files:")
    print("=" * 60)
    
    for filepath, vars_list in sorted(env_vars_by_file.items()):
        print(f"\n📄 {filepath}:")
        for var in vars_list:
            print(f"  • {var}")
    
    print(f"\n📋 All unique variables (alphabetical, because we're civilized):")
    for var in sorted(all_env_vars):
        print(f"  {var}")
    
    # Bonus: Check which ones are actually set - the plot twist!
    print(f"\n🔧 Currently set in your environment (the ones that actually work):")
    set_vars = [var for var in all_env_vars if var in os.environ]
    for var in sorted(set_vars):
        print(f"  ✓ {var}")
    
    missing = all_env_vars - set(set_vars)
    if missing:
        print(f"\n⚠️  Not set (the ones that will break in production):")
        for var in sorted(missing):
            print(f"  ✗ {var}")

if __name__ == "__main__":
    main()
