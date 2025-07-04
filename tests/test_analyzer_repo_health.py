import pytest
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.services.repo_health import check_github_health, check_gitlab_health
from analyzer.models.schemas import Policy, HealthCheckResult


class TestRepoHealth:
    """Test repository health checking functionality"""

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_github_health_success(self, mock_get):
        """Test successful GitHub health check"""
        # Mock repository response
        repo_response = Mock()
        repo_response.raise_for_status.return_value = None
        repo_response.json.return_value = {
            "pushed_at": "2021-01-01T12:00:00Z",
            "stargazers_count": 100,
            "forks_count": 50
        }
        
        # Mock issues response
        issues_response = Mock()
        issues_response.raise_for_status.return_value = None
        issues_response.json.return_value = [{"id": 1}, {"id": 2}]  # 2 open issues
        
        # Mock contents response
        contents_response = Mock()
        contents_response.status_code = 200
        contents_response.json.return_value = [
            {"name": "README.md"},
            {"name": "LICENSE"},
            {"name": "main.py"}
        ]
        
        mock_get.side_effect = [repo_response, issues_response, contents_response]
        
        policy = Policy(max_inactive_days=365, require_license=True, require_readme=True)
        result = check_github_health("user", "repo", policy, token="test_token")
        
        assert result.repository_url == "https://github.com/user/repo"
        assert result.platform == "github"
        assert result.owner == "user"
        assert result.repo_name == "repo"
        assert result.last_activity == "2021-01-01T12:00:00Z"
        assert result.open_issues_count == 2
        assert result.stars_count == 100
        assert result.forks_count == 50
        assert result.has_readme is True
        assert result.has_license is True
        assert result.is_healthy is False  # Due to inactivity
        assert len(result.warnings) > 0

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_github_health_network_error(self, mock_get):
        """Test GitHub health check with network error"""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Network error")
        
        policy = Policy()
        result = check_github_health("user", "repo", policy)
        
        assert result.is_healthy is False
        assert len(result.errors) > 0
        assert "Error checking GitHub repository" in result.errors[0]

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_github_health_missing_files(self, mock_get):
        """Test GitHub health check when README/LICENSE missing"""
        # Mock repository response
        repo_response = Mock()
        repo_response.raise_for_status.return_value = None
        repo_response.json.return_value = {
            "pushed_at": "2024-01-01T12:00:00Z",  # Recent activity
            "stargazers_count": 100,
            "forks_count": 50
        }
        
        # Mock issues response
        issues_response = Mock()
        issues_response.raise_for_status.return_value = None
        issues_response.json.return_value = []
        
        # Mock contents response - no README or LICENSE
        contents_response = Mock()
        contents_response.status_code = 200
        contents_response.json.return_value = [{"name": "main.py"}]
        
        mock_get.side_effect = [repo_response, issues_response, contents_response]
        
        policy = Policy(max_inactive_days=365, require_license=True, require_readme=True)
        result = check_github_health("user", "repo", policy)
        
        assert result.has_readme is False
        assert result.has_license is False
        assert result.is_healthy is False
        assert "No README file found" in result.warnings
        assert "No LICENSE file found" in result.warnings

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_github_health_90_day_warning(self, mock_get):
        """Test GitHub health check with 90 day inactivity warning"""
        # Mock repository response with activity more than 90 but less than 365 days ago
        from datetime import datetime, timezone
        from analyzer.services.repo_health import parse_iso8601_timestamp
        
        # Calculate a date that's about 180 days ago
        import datetime as dt
        now = dt.datetime.now(dt.timezone.utc)
        past_date = now - dt.timedelta(days=180)
        past_date_str = past_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        repo_response = Mock()
        repo_response.raise_for_status.return_value = None
        repo_response.json.return_value = {
            "pushed_at": past_date_str,
            "stargazers_count": 100,
            "forks_count": 50
        }
        
        # Mock issues response
        issues_response = Mock()
        issues_response.raise_for_status.return_value = None
        issues_response.json.return_value = []
        
        # Mock contents response
        contents_response = Mock()
        contents_response.status_code = 200
        contents_response.json.return_value = [
            {"name": "README.md"},
            {"name": "LICENSE"}
        ]
        
        mock_get.side_effect = [repo_response, issues_response, contents_response]
        
        policy = Policy(max_inactive_days=365, require_license=False, require_readme=False)
        result = check_github_health("user", "repo", policy)
        
        assert "Repository has been inactive for over 90 days" in result.warnings

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_gitlab_health_success(self, mock_get):
        """Test successful GitLab health check"""
        # Use a more recent date to ensure the repo is considered healthy
        import datetime as dt
        now = dt.datetime.now(dt.timezone.utc)
        recent_date = now - dt.timedelta(days=30)  # 30 days ago
        recent_date_str = recent_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Mock project response
        project_response = Mock()
        project_response.raise_for_status.return_value = None
        project_response.json.return_value = {
            "last_activity_at": recent_date_str,
            "star_count": 75,
            "forks_count": 25,
            "default_branch": "main"
        }
        
        # Mock issues response
        issues_response = Mock()
        issues_response.raise_for_status.return_value = None
        issues_response.json.return_value = [{"id": 1}]  # 1 open issue
        
        # Mock README file response
        readme_response = Mock()
        readme_response.status_code = 200
        
        # Mock LICENSE file response
        license_response = Mock()
        license_response.status_code = 200
        
        mock_get.side_effect = [
            project_response, 
            issues_response, 
            readme_response,  # README.md check
            license_response  # LICENSE check
        ]
        
        policy = Policy(max_inactive_days=365, require_license=True, require_readme=True)
        result = check_gitlab_health("group", "project", policy, token="test_token")
        
        assert result.repository_url == "https://gitlab.com/group/project"
        assert result.platform == "gitlab"
        assert result.owner == "group"
        assert result.repo_name == "project"
        assert result.last_activity == recent_date_str
        assert result.open_issues_count == 1
        assert result.stars_count == 75
        assert result.forks_count == 25
        assert result.has_readme is True
        assert result.has_license is True
        assert result.is_healthy is True

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_gitlab_health_missing_files(self, mock_get):
        """Test GitLab health check when README/LICENSE missing"""
        # Mock project response
        project_response = Mock()
        project_response.raise_for_status.return_value = None
        project_response.json.return_value = {
            "last_activity_at": "2024-01-01T12:00:00Z",
            "star_count": 75,
            "forks_count": 25,
            "default_branch": "main"
        }
        
        # Mock issues response
        issues_response = Mock()
        issues_response.raise_for_status.return_value = None
        issues_response.json.return_value = []
        
        # Mock file responses - all return 404 (not found)
        file_not_found_response = Mock()
        file_not_found_response.status_code = 404
        
        # There are multiple README and LICENSE file checks, so mock many 404s
        mock_get.side_effect = [
            project_response, 
            issues_response
        ] + [file_not_found_response] * 20  # Many file checks
        
        policy = Policy(max_inactive_days=365, require_license=True, require_readme=True)
        result = check_gitlab_health("group", "project", policy)
        
        assert result.has_readme is False
        assert result.has_license is False
        assert result.is_healthy is False
        assert "No README file found" in result.warnings
        assert "No LICENSE file found" in result.warnings

    @patch('analyzer.services.repo_health.requests.get')
    def test_check_gitlab_health_network_error(self, mock_get):
        """Test GitLab health check with network error"""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Network error")
        
        policy = Policy()
        result = check_gitlab_health("group", "project", policy)
        
        assert result.is_healthy is False
        assert len(result.errors) > 0
        assert "Error checking GitLab repository" in result.errors[0]