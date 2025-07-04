import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.services.package_info import (
    get_library_info,
    get_npm_info,
    parse_repo_url,
    extract_repo_info,
    extract_npm_repo_info,
    get_latest_version_release_date
)


class TestPackageInfoExtended:
    """Extended tests for package info functionality"""

    def test_get_npm_info_invalid_name(self):
        """Test npm package info with invalid name"""
        with pytest.raises(ValueError):
            get_npm_info("invalid@name")

    @patch('analyzer.services.package_info.requests.get')
    def test_get_npm_info_failure(self, mock_get):
        """Test failed npm package info retrieval"""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Network error")

        result = get_npm_info("nonexistent")

        assert result is None

    def test_parse_repo_url_git_prefix(self):
        """Test parsing repository URL with git+ prefix"""
        url = "git+https://github.com/user/repo.git"
        platform, org, repo = parse_repo_url(url)

        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_parse_repo_url_bitbucket(self):
        """Test parsing Bitbucket repository URL"""
        url = "https://bitbucket.org/user/repo"
        platform, org, repo = parse_repo_url(url)

        assert platform == "bitbucket"
        assert org == "user"
        assert repo == "repo"

    def test_parse_repo_url_subdomain_github(self):
        """Test parsing GitHub Enterprise subdomain URL"""
        url = "https://github.example.com/user/repo"
        platform, org, repo = parse_repo_url(url)

        # The current implementation only recognizes exact github.com domains
        assert platform is None
        assert org is None
        assert repo is None

    def test_parse_repo_url_subdomain_gitlab(self):
        """Test parsing GitLab self-hosted subdomain URL"""
        url = "https://gitlab.example.com/group/project"
        platform, org, repo = parse_repo_url(url)

        # The current implementation only recognizes exact gitlab.com domains
        assert platform is None
        assert org is None
        assert repo is None

    def test_parse_repo_url_insufficient_path_parts(self):
        """Test parsing URL with insufficient path parts"""
        url = "https://github.com/user"
        platform, org, repo = parse_repo_url(url)

        assert platform is None
        assert org is None
        assert repo is None

    def test_extract_repo_info_no_project_urls(self):
        """Test extracting repo info when project_urls is missing"""
        info = {"name": "test-package"}

        repo_url, platform, org, repo = extract_repo_info(info)

        assert repo_url is None
        assert platform is None
        assert org is None
        assert repo is None

    def test_extract_repo_info_secondary_types(self):
        """Test extracting repo info using secondary URL types"""
        info = {
            "project_urls": {
                "Documentation": "https://docs.example.com",
                "Homepage": "https://github.com/user/repo",
                "Bug Tracker": "https://github.com/user/repo/issues"
            }
        }

        repo_url, platform, org, repo = extract_repo_info(info)

        assert repo_url == "https://github.com/user/repo"
        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_extract_repo_info_fallback_types(self):
        """Test extracting repo info using fallback URL types"""
        info = {
            "project_urls": {
                "Documentation": "https://docs.example.com",
                "Bug Tracker": "https://github.com/user/repo/issues",
                "Funding": "https://sponsor.example.com",
                "Custom": "https://github.com/user/repo"
            }
        }

        repo_url, platform, org, repo = extract_repo_info(info)

        assert repo_url == "https://github.com/user/repo"
        assert platform == "github"
        assert org == "user"
        assert repo == "repo"

    def test_extract_repo_info_excluded_types_only(self):
        """Test extracting repo info when only excluded URL types exist"""
        info = {
            "project_urls": {
                "Funding": "https://sponsor.example.com",
                "Donate": "https://donate.example.com",
                "Documentation": "https://docs.example.com"
            }
        }

        repo_url, platform, org, repo = extract_repo_info(info)

        assert repo_url is None
        assert platform is None
        assert org is None
        assert repo is None

    def test_extract_npm_repo_info_no_repository(self):
        """Test extracting npm repo info when repository field is missing"""
        info = {"name": "test-package"}

        repo_url, platform, org, repo = extract_npm_repo_info(info)

        assert repo_url is None
        assert platform is None
        assert org is None
        assert repo is None

    def test_extract_npm_repo_info_no_url(self):
        """Test extracting npm repo info when repository URL is missing"""
        info = {
            "repository": {
                "type": "git"
                # url field is missing
            }
        }

        repo_url, platform, org, repo = extract_npm_repo_info(info)

        assert repo_url is None
        assert platform is None
        assert org is None
        assert repo is None

    def test_get_latest_version_release_date_no_info(self):
        """Test getting release date when info is missing"""
        result = get_latest_version_release_date({})

        assert result is None

    def test_get_latest_version_release_date_no_version(self):
        """Test getting release date when version info is missing"""
        info = {"releases": {}}

        result = get_latest_version_release_date(info)

        assert result is None

    def test_get_latest_version_release_date_version_not_in_releases(self):
        """Test getting release date when version not found in releases"""
        info = {
            "info": {"version": "2.0.0"},
            "releases": {"1.0.0": [{"upload_time_iso_8601": "2021-01-01T12:00:00Z"}]}
        }

        result = get_latest_version_release_date(info)

        assert result is None

    def test_get_latest_version_release_date_empty_releases_list(self):
        """Test getting release date when releases list is empty"""
        info = {
            "info": {"version": "1.0.0"},
            "releases": {"1.0.0": []}
        }

        result = get_latest_version_release_date(info)

        assert result is None