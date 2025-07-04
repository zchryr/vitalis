import pytest
import json
import tempfile
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.extractor.requirements_txt import extract_requirements_txt
from extractor.extractor.environment_yml import extract_environment_yml
from extractor.extractor.pyproject_toml import extract_pyproject_toml
from extractor.extractor.package_json import extract_package_json
from extractor.extractor.poetry_lock import extract_poetry_lock
from core.models import Dependency


class TestRequirementsTxt:
    """Test requirements.txt extraction"""

    def test_extract_requirements_txt_with_versions(self):
        """Test extracting requirements.txt with version specifiers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('requests==2.25.0\ndjango>=3.2.0\nflask~=2.0.0\n')

            result = extract_requirements_txt(test_file)

            assert len(result) == 3
            assert result[0].name == 'requests'
            assert result[0].version == '2.25.0'
            assert result[0].source == 'pypi'
            assert result[1].name == 'django'
            assert result[1].version == '3.2.0'

    def test_extract_requirements_txt_without_versions(self):
        """Test extracting requirements.txt without version specifiers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('requests\ndjango\n')

            result = extract_requirements_txt(test_file)

            assert len(result) == 2
            assert result[0].name == 'requests'
            assert result[0].version is None
            assert result[1].name == 'django'
            assert result[1].version is None

    def test_extract_requirements_txt_with_comments(self):
        """Test extracting requirements.txt with comments and empty lines"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('# This is a comment\nrequests==2.25.0\n\n# Another comment\ndjango>=3.2.0\n')

            result = extract_requirements_txt(test_file)

            assert len(result) == 2
            assert result[0].name == 'requests'
            assert result[1].name == 'django'


class TestEnvironmentYml:
    """Test environment.yml extraction"""

    def test_extract_environment_yml_conda_deps(self):
        """Test extracting conda dependencies from environment.yml"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'environment.yml')
            with open(test_file, 'w') as f:
                f.write("""name: test-env
dependencies:
  - python=3.9
  - numpy=1.20.0
  - pandas
""")

            result = extract_environment_yml(test_file)

            assert len(result) == 3
            assert result[0].name == 'python'
            assert result[0].version == '3.9'
            assert result[0].source == 'conda'
            assert result[1].name == 'numpy'
            assert result[1].version == '1.20.0'
            assert result[2].name == 'pandas'
            assert result[2].version is None

    def test_extract_environment_yml_pip_deps(self):
        """Test extracting pip dependencies from environment.yml"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'environment.yml')
            with open(test_file, 'w') as f:
                f.write("""name: test-env
dependencies:
  - python=3.9
  - pip:
    - requests==2.25.0
    - django==3.2.0
""")

            result = extract_environment_yml(test_file)

            assert len(result) == 3
            assert result[0].name == 'python'
            assert result[0].source == 'conda'
            assert result[1].name == 'requests'
            assert result[1].version == '2.25.0'
            assert result[1].source == 'pip'
            assert result[2].name == 'django'
            assert result[2].version == '3.2.0'
            assert result[2].source == 'pip'


class TestPyprojectToml:
    """Test pyproject.toml extraction"""

    def test_extract_pyproject_toml_poetry_deps(self):
        """Test extracting Poetry dependencies from pyproject.toml"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'pyproject.toml')
            with open(test_file, 'w') as f:
                f.write("""[tool.poetry]
name = "test-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.25.0"
django = {version = "^3.2.0", extras = ["dev"]}
""")

            result = extract_pyproject_toml(test_file)

            assert len(result) == 2  # python is skipped
            assert result[0].name == 'requests'
            assert result[0].version == '^2.25.0'
            assert result[0].source == 'poetry'
            assert result[1].name == 'django'
            assert result[1].version == '^3.2.0'


class TestPackageJson:
    """Test package.json extraction"""

    def test_extract_package_json_deps(self):
        """Test extracting dependencies from package.json"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'package.json')
            with open(test_file, 'w') as f:
                f.write("""{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "mocha": "^8.3.2"
  }
}""")

            result = extract_package_json(test_file)

            assert len(result) == 3
            assert result[0].name == 'express'
            assert result[0].version == '^4.17.1'
            assert result[0].source == 'npm'
            assert result[1].name == 'lodash'
            assert result[1].version == '^4.17.21'
            assert result[2].name == 'mocha'
            assert result[2].version == '^8.3.2'


class TestPoetryLock:
    """Test poetry.lock extraction"""

    def test_extract_poetry_lock_deps(self):
        """Test extracting dependencies from poetry.lock"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'poetry.lock')
            with open(test_file, 'w') as f:
                f.write("""[[package]]
name = "requests"
version = "2.25.0"
category = "main"
description = "Python HTTP for Humans."

[[package]]
name = "pytest"
version = "6.2.0"
category = "dev"
description = "pytest: simple powerful testing with Python"

[[package]]
name = "django"
version = "3.2.0"
category = "main"
description = "Django web framework"
""")

            result = extract_poetry_lock(test_file)

            assert len(result) == 2  # Only main category packages
            assert result[0].name == 'requests'
            assert result[0].version == '2.25.0'
            assert result[0].source == 'poetry.lock'
            assert result[1].name == 'django'
            assert result[1].version == '3.2.0'