import json
from core.models import Dependency
from typing import List, Dict, Any

def extract_package_json(path: str) -> List[Dependency]:
    """Extract dependencies from a package.json file.
    
    Parses a package.json file and extracts both regular dependencies and
    development dependencies from the respective sections.
    
    Args:
        path: Path to the package.json file.
        
    Returns:
        List of Dependency objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the package.json file does not exist.
        json.JSONDecodeError: If the JSON file is malformed.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    dependencies: List[Dependency] = []
    with open(path, 'r', encoding='utf-8') as f:
        data: Dict[str, Any] = json.load(f)
    for section in ['dependencies', 'devDependencies']:
        for name, version in data.get(section, {}).items():
            dependencies.append(Dependency(name=name, version=version, source='npm', raw=f'{name}: {version}'))
    return dependencies