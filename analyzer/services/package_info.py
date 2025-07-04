import re
import requests
from typing import Dict, Optional, Tuple, Any, List
from urllib.parse import urlparse

def get_library_info(library_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch package metadata from PyPI for a given library name.
    Args:
        library_name (str): The name of the library to fetch.
    Returns:
        dict or None: The package metadata as a dictionary, or None if not found or error.
    Raises:
        ValueError: If the library name is invalid.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", library_name):
        raise ValueError("Invalid library name. Only alphanumeric characters, dashes, and underscores are allowed.")
    url: str = f"https://pypi.org/pypi/{library_name}/json"
    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        json_data: Dict[str, Any] = response.json()
        return json_data
    except requests.exceptions.RequestException:
        return None

def get_npm_info(package_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch package metadata from npm registry for a given package name.
    Args:
        package_name (str): The name of the npm package.
    Returns:
        dict or None: The package metadata as a dictionary, or None if not found or error.
    Raises:
        ValueError: If the package name is invalid.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", package_name):
        raise ValueError("Invalid package name. Only alphanumeric characters, dashes, and underscores are allowed.")
    url: str = f"https://registry.npmjs.org/{package_name}"
    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        json_data: Dict[str, Any] = response.json()
        return json_data
    except requests.exceptions.RequestException:
        return None

def parse_repo_url(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a repository URL and extract the platform, organization, and repository name.
    Args:
        url (str): The repository URL.
    Returns:
        tuple: (platform, org, repo) or (None, None, None) if not recognized.
    """
    if url.startswith('git+'):
        url = url[4:]
    parsed_url = urlparse(url)
    path_parts: List[str] = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2:
        org = path_parts[0]
        repo = path_parts[1]
        repo = repo.replace('.git', '')
        if parsed_url.netloc.endswith('.github.com') or parsed_url.netloc == 'github.com':
            return 'github', org, repo
        elif parsed_url.netloc.endswith('.gitlab.com') or parsed_url.netloc == 'gitlab.com':
            return 'gitlab', org, repo
        elif parsed_url.netloc.endswith('.bitbucket.org') or parsed_url.netloc == 'bitbucket.org':
            return 'bitbucket', org, repo
    return None, None, None

def extract_repo_info(info: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract the repository URL and its platform/org/repo from PyPI project metadata.
    Args:
        info (dict): The PyPI project info dictionary.
    Returns:
        tuple: (repo_url, platform, org, repo) or (None, None, None, None) if not found.
    """
    if not info or "project_urls" not in info:
        return None, None, None, None
    primary_repo_types = ["Source", "Repository", "Code"]
    secondary_repo_types = ["Homepage"]
    # Prefer primary repo types
    for url_type, url in info["project_urls"].items():
        if url_type in primary_repo_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo
    # Fallback to secondary repo types
    for url_type, url in info["project_urls"].items():
        if url_type in secondary_repo_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo
    # Fallback to any other URL except excluded types
    excluded_types = ["Funding", "Sponsor", "Donate", "Bug Tracker", "Issue Tracker", "Documentation"]
    for url_type, url in info["project_urls"].items():
        if url_type not in excluded_types:
            platform, org, repo = parse_repo_url(url)
            if platform:
                return url, platform, org, repo
    return None, None, None, None

def extract_npm_repo_info(info: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract the repository URL and its platform/org/repo from npm package metadata.
    Args:
        info (dict): The npm package info dictionary.
    Returns:
        tuple: (repo_url, platform, org, repo) or (None, None, None, None) if not found.
    """
    if not info or "repository" not in info:
        return None, None, None, None
    repo_url = info["repository"].get("url")
    if not repo_url:
        return None, None, None, None
    platform, org, repo = parse_repo_url(repo_url)
    return repo_url, platform, org, repo

def get_latest_version_release_date(info: Dict[str, Any]) -> Optional[str]:
    """
    Get the release date of the latest version from PyPI package metadata.
    Args:
        info (dict): The PyPI package metadata.
    Returns:
        str or None: The ISO 8601 release date string, or None if not found.
    """
    if not info or "releases" not in info:
        return None
    latest_version = info.get("info", {}).get("version")
    if not latest_version or latest_version not in info["releases"]:
        return None
    releases = info["releases"][latest_version]
    if not releases:
        return None
    upload_time: Optional[str] = releases[0].get("upload_time_iso_8601")
    return upload_time