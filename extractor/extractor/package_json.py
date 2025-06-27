import json
from core.models import Dependency
from typing import List

def extract_package_json(path: str) -> List[Dependency]:
    dependencies = []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for section in ['dependencies', 'devDependencies']:
        for name, version in data.get(section, {}).items():
            dependencies.append(Dependency(name=name, version=version, source='npm', raw=f'{name}: {version}'))
    return dependencies