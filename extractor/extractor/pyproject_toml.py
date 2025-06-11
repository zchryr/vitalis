import toml
from extractor.models import Dependency
from typing import List

def extract_pyproject_toml(path: str) -> List[Dependency]:
    dependencies = []
    data = toml.load(path)
    poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    for name, version in poetry_deps.items():
        if name.lower() == 'python':
            continue
        if isinstance(version, dict):
            version_str = version.get('version')
        else:
            version_str = version
        dependencies.append(Dependency(name=name, version=version_str, source='poetry', raw=f'{name}: {version_str}'))
    return dependencies