import pytest
import json
import tempfile
import os
import sys
from unittest.mock import patch, Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.services.dependency_extractor import (
    extract_requirements_txt_from_content,
    extract_package_json_from_content,
    extract_pyproject_toml_from_content,
    extract_environment_yml_from_content,
    extract_poetry_lock_from_content
)
from analyzer.services.package_info import (
    get_library_info,
    get_npm_info,
    parse_repo_url,
    extract_repo_info,
    extract_npm_repo_info,
    get_latest_version_release_date
)
from analyzer.utils.helpers import parse_iso8601_timestamp
from core.models import Dependency
from datetime import datetime, timezone


class TestDependencyExtractor:
    """Test dependency extraction from content strings"""

    def test_extract_requirements_txt_from_content(self):
        """Test extracting requirements.txt from content string"""
        content = "requests==2.25.0\ndjango>=3.2.0\n# comment\nflask"
        result = extract_requirements_txt_from_content(content)

        assert len(result) == 3
        assert result[0].name == 'requests'
        assert result[0].version == '2.25.0'
        assert result[0].source == 'pypi'
        assert result[1].name == 'django'
        assert result[1].version == '3.2.0'
        assert result[2].name == 'flask'
        assert result[2].version is None

    def test_extract_package_json_from_content(self):
        """Test extracting package.json from content string"""
        content = """{
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "mocha": "^8.3.2"
  }
}"""
        result = extract_package_json_from_content(content)

        assert len(result) == 3
        assert result[0].name == 'express'
        assert result[0].version == '^4.17.1'
        assert result[0].source == 'npm'

    def test_extract_pyproject_toml_from_content(self):
        """Test extracting pyproject.toml from content string"""
        content = """[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.25.0"
django = {version = "^3.2.0", extras = ["dev"]}
"""
        result = extract_pyproject_toml_from_content(content)

        assert len(result) == 2  # python is skipped
        assert result[0].name == 'requests'
        assert result[0].version == '^2.25.0'
        assert result[0].source == 'poetry'

    def test_extract_environment_yml_from_content(self):
        """Test extracting environment.yml from content string"""
        content = """name: test-env
dependencies:
  - python=3.9
  - numpy=1.20.0
  - pip:
    - requests==2.25.0
"""
        result = extract_environment_yml_from_content(content)

        assert len(result) == 3
        assert result[0].name == 'python'
        assert result[0].source == 'conda'
        assert result[2].name == 'requests'
        assert result[2].source == 'pip'

    def test_extract_poetry_lock_from_content(self):
        """Test extracting poetry.lock from content string"""
        content = """[[package]]
name = "requests"
version = "2.25.0"
category = "main"

[[package]]
name = "pytest"
version = "6.2.0"
category = "dev"
"""
        result = extract_poetry_lock_from_content(content)

        assert len(result) == 1  # only main category
        assert result[0].name == 'requests'
        assert result[0].version == '2.25.0'
        assert result[0].source == 'poetry.lock'


class TestPackageInfo:
    """Test package information retrieval"""

    @patch('analyzer.services.package_info.requests.get')
    def test_get_library_info_success(self, mock_get):
        """Test successful PyPI library info retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"info": {"name": "requests", "version": "2.25.0"}}
        mock_get.return_value = mock_response

        result = get_library_info("requests")

        assert result is not None
        assert result["info"]["name"] == "requests"
        mock_get.assert_called_once_with("https://pypi.org/pypi/requests/json")

    @patch('analyzer.services.package_info.requests.get')
    def test_get_library_info_failure(self, mock_get):
        """Test failed PyPI library info retrieval"""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Network error")

        result = get_library_info("nonexistent")

        assert result is None

    def test_get_library_info_invalid_name(self):
        """Test PyPI library info with invalid name"""
        with pytest.raises(ValueError):
            get_library_info("invalid@name")

    @patch('analyzer.services.package_info.requests.get')
    def test_get_npm_info_success(self, mock_get):
        """Test successful npm package info retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"name": "express", "version": "4.17.1"}
        mock_get.return_value = mock_response

        result = get_npm_info("express")

        assert result is not None
        assert result["name"] == "express"
        mock_get.assert_called_once_with("https://registry.npmjs.org/express")

    def test_parse_repo_url_github(self):
        """Test parsing GitHub repository URL"""
        url = "https://github.com/user/repo"
        platform, org, repo = parse_repo_url(url)

        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_parse_repo_url_gitlab(self):
        """Test parsing GitLab repository URL"""
        url = "https://gitlab.com/group/project.git"
        platform, org, repo = parse_repo_url(url)

        assert platform == "gitlab"
        assert org == "group"
        assert repo == "project"

    def test_parse_repo_url_invalid(self):
        """Test parsing invalid repository URL"""
        url = "https://example.com/not/a/repo"
        platform, org, repo = parse_repo_url(url)

        assert platform is None
        assert org is None
        assert repo is None

    def test_extract_repo_info(self):
        """Test extracting repository info from PyPI project data"""
        info = {
            "project_urls": {
                "Homepage": "https://example.com",
                "Source": "https://github.com/user/repo",
                "Bug Tracker": "https://github.com/user/repo/issues"
            }
        }

        repo_url, platform, org, repo = extract_repo_info(info)

        assert repo_url == "https://github.com/user/repo"
        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_extract_npm_repo_info(self):
        """Test extracting repository info from npm package data"""
        info = {
            "repository": {
                "type": "git",
                "url": "git+https://github.com/user/repo.git"
            }
        }

        repo_url, platform, org, repo = extract_npm_repo_info(info)

        assert repo_url == "git+https://github.com/user/repo.git"
        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_get_latest_version_release_date(self):
        """Test getting latest version release date"""
        info = {
            "info": {"version": "2.25.0"},
            "releases": {
                "2.25.0": [
                    {"upload_time_iso_8601": "2021-01-01T12:00:00Z"}
                ]
            }
        }

        result = get_latest_version_release_date(info)

        assert result == "2021-01-01T12:00:00Z"

    def test_get_latest_version_release_date_no_releases(self):
        """Test getting release date when no releases exist"""
        info = {"info": {"version": "1.0.0"}, "releases": {}}

        result = get_latest_version_release_date(info)

        assert result is None


class TestHelpers:
    """Test utility helper functions"""

    def test_parse_iso8601_timestamp_with_milliseconds(self):
        """Test parsing ISO 8601 timestamp with milliseconds"""
        timestamp = "2021-01-01T12:00:00.123Z"
        result = parse_iso8601_timestamp(timestamp)

        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == timezone.utc

    def test_parse_iso8601_timestamp_without_milliseconds(self):
        """Test parsing ISO 8601 timestamp without milliseconds"""
        timestamp = "2021-01-01T12:00:00Z"
        result = parse_iso8601_timestamp(timestamp)

        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == timezone.utc

    def test_parse_iso8601_timestamp_invalid(self):
        """Test parsing invalid timestamp format"""
        with pytest.raises(ValueError):
            parse_iso8601_timestamp("invalid-timestamp")