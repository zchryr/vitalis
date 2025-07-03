import yaml
from core.models import Dependency
from typing import List, Any, Dict, Union

def extract_environment_yml(path: str) -> List[Dependency]:
    """Extract dependencies from a Conda environment.yml file.
    
    Parses a Conda environment.yml file and extracts both conda and pip dependencies.
    Supports both string-format dependencies and pip sub-sections.
    
    Args:
        path: Path to the environment.yml file.
        
    Returns:
        List of Dependency objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the environment.yml file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
    """
    dependencies: List[Dependency] = []
    with open(path, 'r', encoding='utf-8') as f:
        data: Dict[str, Any] = yaml.safe_load(f)
    for dep in data.get('dependencies', []):
        if isinstance(dep, str):
            # Conda dependency
            name, *version = dep.split('=')
            dependencies.append(Dependency(name=name.strip(), version='='.join(version) if version else None, source='conda', raw=dep))
        elif isinstance(dep, dict) and 'pip' in dep:
            pip_deps: List[str] = dep['pip']
            for pip_dep in pip_deps:
                name, *version = pip_dep.split('==')
                dependencies.append(Dependency(name=name.strip(), version=version[0] if version else None, source='pip', raw=pip_dep))
    return dependencies