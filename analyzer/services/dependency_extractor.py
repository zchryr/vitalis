import re
import json
import toml
import yaml
from typing import List
from core.models import Dependency

def extract_requirements_txt_from_content(content: str) -> List[Dependency]:
    """
    Parse a requirements.txt file content and extract dependencies as Dependency objects.
    Args:
        content (str): The content of the requirements.txt file.
    Returns:
        List[Dependency]: List of extracted dependencies.
    """
    dependencies = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue  # Skip empty lines and comments
        match = re.match(r'([^=<>~!]+)([=<>~!]+)(.+)', line)
        if match:
            name = match.group(1).strip()
            version = match.group(3).strip()
            dependencies.append(Dependency(name=name, version=version, source='pypi', raw=line))
        else:
            dependencies.append(Dependency(name=line, source='pypi', raw=line))
    return dependencies

def extract_package_json_from_content(content: str) -> List[Dependency]:
    """
    Parse a package.json file content and extract dependencies as Dependency objects.
    Args:
        content (str): The content of the package.json file.
    Returns:
        List[Dependency]: List of extracted dependencies.
    """
    dependencies = []
    data = json.loads(content)
    for section in ['dependencies', 'devDependencies']:
        for name, version in data.get(section, {}).items():
            dependencies.append(Dependency(name=name, version=version, source='npm', raw=f'{name}: {version}'))
    return dependencies

def extract_pyproject_toml_from_content(content: str) -> List[Dependency]:
    """
    Parse a pyproject.toml file content and extract dependencies as Dependency objects.
    Args:
        content (str): The content of the pyproject.toml file.
    Returns:
        List[Dependency]: List of extracted dependencies.
    """
    dependencies = []
    data = toml.loads(content)
    poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    for name, version in poetry_deps.items():
        if name.lower() == 'python':
            continue  # Skip the Python version itself
        if isinstance(version, dict):
            version_str = version.get('version')
        else:
            version_str = version
        dependencies.append(Dependency(name=name, version=version_str, source='poetry', raw=f'{name}: {version_str}'))
    return dependencies

def extract_environment_yml_from_content(content: str) -> List[Dependency]:
    """
    Parse an environment.yml file content and extract dependencies as Dependency objects.
    Args:
        content (str): The content of the environment.yml file.
    Returns:
        List[Dependency]: List of extracted dependencies.
    """
    dependencies = []
    data = yaml.safe_load(content)
    for dep in data.get('dependencies', []):
        if isinstance(dep, str):
            # Conda dependency
            name, *version = dep.split('=')
            dependencies.append(Dependency(name=name.strip(), version='='.join(version) if version else None, source='conda', raw=dep))
        elif isinstance(dep, dict) and 'pip' in dep:
            # Pip dependencies inside environment.yml
            for pip_dep in dep['pip']:
                name, *version = pip_dep.split('==')
                dependencies.append(Dependency(name=name.strip(), version=version[0] if version else None, source='pip', raw=pip_dep))
    return dependencies

def extract_poetry_lock_from_content(content: str) -> List[Dependency]:
    """
    Parse a poetry.lock file content and extract main dependencies as Dependency objects.
    Args:
        content (str): The content of the poetry.lock file.
    Returns:
        List[Dependency]: List of extracted dependencies.
    """
    dependencies = []
    import re as _re
    # Split the file into package blocks
    packages = _re.split(r'\n\[\[package\]\]\n', content)
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