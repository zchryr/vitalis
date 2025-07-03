from core.models import Dependency
from typing import List, Optional
import re

def extract_requirements_txt(path: str) -> List[Dependency]:
    """Extract dependencies from a requirements.txt file.
    
    Parses a requirements.txt file and extracts package names and versions.
    Supports various version specifiers like ==, >=, <=, ~=, >, <, =.
    
    Args:
        path: Path to the requirements.txt file.
        
    Returns:
        List of Dependency objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the requirements.txt file does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    dependencies: List[Dependency] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Split on '==' or '>=' or '<=' or '~=' or '>' or '<' or '='
            match = re.match(r'([^=<>~!]+)([=<>~!]+)(.+)', line)
            if match:
                name = match.group(1).strip()
                version = match.group(3).strip()
                dependencies.append(Dependency(name=name, version=version, source='pypi', raw=line))
            else:
                dependencies.append(Dependency(name=line, source='pypi', raw=line))
    return dependencies