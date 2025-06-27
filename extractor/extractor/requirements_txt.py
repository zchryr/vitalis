from core.models import Dependency
from typing import List

def extract_requirements_txt(path: str) -> List[Dependency]:
    dependencies = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Split on '==' or '>=' or '<=' or '~=' or '>' or '<' or '='
            import re
            match = re.match(r'([^=<>~!]+)([=<>~!]+)(.+)', line)
            if match:
                name = match.group(1).strip()
                version = match.group(3).strip()
                dependencies.append(Dependency(name=name, version=version, source='pypi', raw=line))
            else:
                dependencies.append(Dependency(name=line, source='pypi', raw=line))
    return dependencies