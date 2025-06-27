from core.models import Dependency
from typing import List
import re

def extract_poetry_lock(path: str) -> List[Dependency]:
    dependencies = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split into package sections
    packages = re.split(r'\n\[\[package\]\]\n', content)
    for pkg in packages:
        lines = pkg.strip().splitlines()
        name = version = category = None
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