import toml
from core.models import Dependency
from typing import List, Dict, Any, Union

def extract_pyproject_toml(path: str) -> List[Dependency]:
    """Extract dependencies from a pyproject.toml file.
    
    Parses a pyproject.toml file and extracts Poetry dependencies from the
    [tool.poetry.dependencies] section. Skips Python version requirements.
    
    Args:
        path: Path to the pyproject.toml file.
        
    Returns:
        List of Dependency objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the pyproject.toml file does not exist.
        toml.TomlDecodeError: If the TOML file is malformed.
    """
    dependencies: List[Dependency] = []
    data: Dict[str, Any] = toml.load(path)
    poetry_deps: Dict[str, Union[str, Dict[str, Any]]] = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    for name, version in poetry_deps.items():
        if name.lower() == 'python':
            continue
        version_str: Union[str, None]
        if isinstance(version, dict):
            version_str = version.get('version')
        else:
            version_str = version
        dependencies.append(Dependency(name=name, version=version_str, source='poetry', raw=f'{name}: {version_str}'))
    return dependencies