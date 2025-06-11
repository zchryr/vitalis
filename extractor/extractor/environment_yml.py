import yaml
from extractor.models import Dependency
from typing import List

def extract_environment_yml(path: str) -> List[Dependency]:
    dependencies = []
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    for dep in data.get('dependencies', []):
        if isinstance(dep, str):
            # Conda dependency
            name, *version = dep.split('=')
            dependencies.append(Dependency(name=name.strip(), version='='.join(version) if version else None, source='conda', raw=dep))
        elif isinstance(dep, dict) and 'pip' in dep:
            for pip_dep in dep['pip']:
                name, *version = pip_dep.split('==')
                dependencies.append(Dependency(name=name.strip(), version=version[0] if version else None, source='pip', raw=pip_dep))
    return dependencies