from core.models import Dependency
from typing import List, Optional
import re

def extract_poetry_lock(path: str) -> List[Dependency]:
    """Extract dependencies from a poetry.lock file.
    
    Parses a poetry.lock file by splitting it into package sections and
    extracting name, version, and category information. Only includes
    packages marked as 'main' category (production dependencies).
    
    Args:
        path: Path to the poetry.lock file.
        
    Returns:
        List of Dependency objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the poetry.lock file does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    dependencies: List[Dependency] = []
    with open(path, 'r', encoding='utf-8') as f:
        content: str = f.read()
    # Split into package sections
    packages: List[str] = re.split(r'\n\[\[package\]\]\n', content)
    for pkg in packages:
        lines: List[str] = pkg.strip().splitlines()
        name: Optional[str] = None
        version: Optional[str] = None
        category: Optional[str] = None
        for line in lines:
            if line.startswith('name = '):
                name = line.split('=', 1)[1].strip().strip('"')
            elif line.startswith('version = '):
                version = line.split('=', 1)[1].strip().strip('"')
            elif line.startswith('category = '):
                category = line.split('=', 1)[1].strip().strip('"')
        if name and category == 'main':
            dependencies.append(Dependency(name=name, version=version, source='poetry.lock', raw=pkg.strip()))
    return dependencies