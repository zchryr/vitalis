import pytest
import json
import tempfile
import os
import sys
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from io import BytesIO

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.main import app
from analyzer.models.schemas import AnalysisRequest, Policy

client = TestClient(app)


class TestAnalyzerMain:
    """Test FastAPI endpoints in analyzer main module"""

    @patch('analyzer.services.package_info.get_library_info')
    @patch('analyzer.services.repo_health.check_github_health')
    def test_analyze_endpoint_requirements_txt(self, mock_health_check, mock_package_info):
        """Test analyze endpoint with requirements.txt content"""
        # Mock package info response
        mock_package_info.return_value = {
            "info": {
                "summary": "Python HTTP library",
                "version": "2.25.0"
            },
            "project_urls": {
                "Source": "https://github.com/psf/requests"
            }
        }
        
        # Mock health check response
        mock_health_result = Mock()
        mock_health_result.dict.return_value = {
            "repository_url": "https://github.com/psf/requests",
            "platform": "github",
            "is_healthy": True,
            "warnings": [],
            "errors": []
        }
        mock_health_check.return_value = mock_health_result

        request_data = {
            "manifest_content": "requests==2.25.0\ndjango>=3.2.0",
            "manifest_type": "requirements.txt",
            "policy": {
                "max_inactive_days": 365,
                "require_license": True,
                "require_readme": True
            }
        }

        response = client.post("/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["dependency"] == "requests"

    def test_analyze_endpoint_unsupported_manifest(self):
        """Test analyze endpoint with unsupported manifest type"""
        request_data = {
            "manifest_content": "some content",
            "manifest_type": "unsupported.txt",
            "policy": {}
        }

        response = client.post("/v1/analyze", json=request_data)

        assert response.status_code == 400
        assert "Unsupported manifest type" in response.json()["detail"]

    @patch('analyzer.services.package_info.get_npm_info')
    def test_analyze_endpoint_package_json(self, mock_npm_info):
        """Test analyze endpoint with package.json content"""
        # Mock npm info response
        mock_npm_info.return_value = {
            "description": "Fast, unopinionated web framework",
            "dist-tags": {"latest": "4.17.1"},
            "repository": {
                "url": "git+https://github.com/expressjs/express.git"
            }
        }

        request_data = {
            "manifest_content": '{"dependencies": {"express": "^4.17.1"}}',
            "manifest_type": "package.json",
            "policy": {}
        }

        response = client.post("/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["dependency"] == "express"

    def test_analyze_file_endpoint_requirements_txt(self):
        """Test analyze file endpoint with requirements.txt file"""
        # Create a temporary requirements.txt file
        content = "requests==2.25.0\ndjango>=3.2.0"
        file_data = BytesIO(content.encode('utf-8'))

        with patch('analyzer.services.package_info.get_library_info') as mock_package_info:
            mock_package_info.return_value = None  # Simulate package not found

            response = client.post(
                "/v1/analyze/file",
                files={"file": ("requirements.txt", file_data, "text/plain")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 2

    def test_analyze_file_endpoint_unsupported_filename(self):
        """Test analyze file endpoint with unsupported filename"""
        content = "some content"
        file_data = BytesIO(content.encode('utf-8'))

        response = client.post(
            "/v1/analyze/file",
            files={"file": ("unsupported.txt", file_data, "text/plain")}
        )

        assert response.status_code == 400
        assert "Could not infer manifest type" in response.json()["detail"]

    def test_analyze_file_endpoint_package_json(self):
        """Test analyze file endpoint with package.json file"""
        content = '{"dependencies": {"express": "^4.17.1"}}'
        file_data = BytesIO(content.encode('utf-8'))

        with patch('analyzer.services.package_info.get_npm_info') as mock_npm_info:
            mock_npm_info.return_value = None  # Simulate package not found

            response = client.post(
                "/v1/analyze/file",
                files={"file": ("package.json", file_data, "application/json")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 1

    def test_analyze_file_endpoint_environment_yml(self):
        """Test analyze file endpoint with environment.yml file"""
        content = """name: test-env
dependencies:
  - python=3.9
  - requests==2.25.0
"""
        file_data = BytesIO(content.encode('utf-8'))

        with patch('analyzer.services.package_info.get_library_info') as mock_package_info:
            mock_package_info.return_value = None

            response = client.post(
                "/v1/analyze/file",
                files={"file": ("environment.yml", file_data, "text/yaml")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    def test_analyze_file_endpoint_pyproject_toml(self):
        """Test analyze file endpoint with pyproject.toml file"""
        content = """[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.25.0"
"""
        file_data = BytesIO(content.encode('utf-8'))

        with patch('analyzer.services.package_info.get_library_info') as mock_package_info:
            mock_package_info.return_value = None

            response = client.post(
                "/v1/analyze/file",
                files={"file": ("pyproject.toml", file_data, "text/plain")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    def test_analyze_file_endpoint_poetry_lock(self):
        """Test analyze file endpoint with poetry.lock file"""
        content = """[[package]]
name = "requests"
version = "2.25.0"
category = "main"
"""
        file_data = BytesIO(content.encode('utf-8'))

        with patch('analyzer.services.package_info.get_library_info') as mock_package_info:
            mock_package_info.return_value = None

            response = client.post(
                "/v1/analyze/file",
                files={"file": ("poetry.lock", file_data, "text/plain")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    @patch('analyzer.services.package_info.get_library_info')
    def test_analyze_conda_package_not_found(self, mock_package_info):
        """Test analyze endpoint with conda package not found in PyPI"""
        mock_package_info.return_value = None

        request_data = {
            "manifest_content": "name: test\ndependencies:\n  - conda-package=1.0.0",
            "manifest_type": "environment.yml",
            "policy": {}
        }

        response = client.post("/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["error"] is True
        assert "conda-only or system package" in data["results"][0]["message"]

    def test_analyze_file_no_filename(self):
        """Test analyze file endpoint with no filename"""
        content = "requests==2.25.0"
        file_data = BytesIO(content.encode('utf-8'))

        # Create file upload without filename
        response = client.post(
            "/v1/analyze/file",
            files={"file": (None, file_data, "text/plain")}
        )

        # FastAPI returns 422 for validation errors, not 400
        assert response.status_code == 422