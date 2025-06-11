import os
import requests
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from ..models.schemas import HealthCheckResult, Policy
from ..utils.helpers import parse_iso8601_timestamp

# Load environment variables from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
GITHUB_API_BASE = "https://api.github.com"
GITLAB_API_BASE = "https://gitlab.com/api/v4"

# Common README and LICENSE file names to check for
README_FILES = [
    "README.md", "README.rst", "README.txt", "README",
    "README.markdown", "README.mdown", "README.mkdn"
]
LICENSE_FILES = [
    "LICENSE", "LICENSE.md", "LICENSE.txt", "LICENSE.markdown", "LICENSE.mdown", "LICENSE.mkdn",
    "COPYING", "COPYING.md", "COPYING.txt", "COPYING.markdown", "COPYING.mdown", "COPYING.mkdn"
]

def check_github_health(owner: str, repo: str, policy: Policy, token: Optional[str] = None) -> HealthCheckResult:
    """
    Check the health of a GitHub repository based on activity, issues, stars, forks, and presence of README/LICENSE.
    Args:
        owner (str): GitHub organization or user.
        repo (str): Repository name.
        policy (Policy): Health policy to enforce.
        token (Optional[str]): GitHub API token for authentication.
    Returns:
        HealthCheckResult: The health check result for the repository.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    # Initialize result object
    result = HealthCheckResult(
        repository_url=f"https://github.com/{owner}/{repo}",
        platform="github",
        owner=owner,
        repo_name=repo
    )
    try:
        # Fetch repository metadata
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, headers=headers)
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        result.last_activity = repo_data.get("pushed_at")
        if result.last_activity:
            # Calculate days since last activity
            last_activity = parse_iso8601_timestamp(result.last_activity)
            now = datetime.now(timezone.utc)
            result.days_since_last_activity = (now - last_activity).days
            if result.days_since_last_activity > policy.max_inactive_days:
                result.warnings.append(f"Repository has been inactive for over {policy.max_inactive_days} days")
                result.is_healthy = False
            elif result.days_since_last_activity > 90:
                result.warnings.append("Repository has been inactive for over 90 days")
        # Fetch open issues
        issues_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers)
        issues_response.raise_for_status()
        result.open_issues_count = len(issues_response.json())
        # Fetch stars and forks count
        result.stars_count = repo_data.get("stargazers_count", 0)
        result.forks_count = repo_data.get("forks_count", 0)
        # Check for README and LICENSE files in repo root
        contents_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"
        contents_response = requests.get(contents_url, headers=headers)
        if contents_response.status_code == 200:
            contents = contents_response.json()
            result.has_readme = any(file["name"].lower() in [r.lower() for r in README_FILES] for file in contents)
            result.has_license = any(file["name"].lower() in [l.lower() for l in LICENSE_FILES] for file in contents)
            if policy.require_readme and not result.has_readme:
                result.warnings.append("No README file found")
                result.is_healthy = False
            if policy.require_license and not result.has_license:
                result.warnings.append("No LICENSE file found")
                result.is_healthy = False
    except requests.exceptions.RequestException as e:
        # Handle network or API errors
        result.errors.append(f"Error checking GitHub repository: {str(e)}")
        result.is_healthy = False
    return result

def check_gitlab_health(owner: str, repo: str, policy: Policy, token: Optional[str] = None) -> HealthCheckResult:
    """
    Check the health of a GitLab repository based on activity, issues, stars, forks, and presence of README/LICENSE.
    Args:
        owner (str): GitLab group or user.
        repo (str): Repository name.
        policy (Policy): Health policy to enforce.
        token (Optional[str]): GitLab API token for authentication.
    Returns:
        HealthCheckResult: The health check result for the repository.
    """
    headers = {}
    if token:
        headers["PRIVATE-TOKEN"] = token
    # Initialize result object
    result = HealthCheckResult(
        repository_url=f"https://gitlab.com/{owner}/{repo}",
        platform="gitlab",
        owner=owner,
        repo_name=repo
    )
    try:
        # Fetch project metadata
        project_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}"
        project_response = requests.get(project_url, headers=headers)
        project_response.raise_for_status()
        project_data = project_response.json()
        result.last_activity = project_data.get("last_activity_at")
        if result.last_activity:
            # Calculate days since last activity
            last_activity = parse_iso8601_timestamp(result.last_activity)
            now = datetime.now(timezone.utc)
            result.days_since_last_activity = (now - last_activity).days
            if result.days_since_last_activity > policy.max_inactive_days:
                result.warnings.append(f"Repository has been inactive for over {policy.max_inactive_days} days")
                result.is_healthy = False
            elif result.days_since_last_activity > 90:
                result.warnings.append("Repository has been inactive for over 90 days")
        # Fetch open issues
        issues_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers)
        issues_response.raise_for_status()
        result.open_issues_count = len(issues_response.json())
        # Fetch stars and forks count
        result.stars_count = project_data.get("star_count", 0)
        result.forks_count = project_data.get("forks_count", 0)
        # Determine default branch for file checks
        default_branch = project_data.get("default_branch", "master")
        # Check for README files
        result.has_readme = False
        for readme_name in README_FILES:
            file_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/repository/files/{requests.utils.quote(readme_name, safe='')}"
            params = {"ref": default_branch}
            file_response = requests.get(file_url, headers=headers, params=params)
            if file_response.status_code == 200:
                result.has_readme = True
                break
        if policy.require_readme and not result.has_readme:
            result.warnings.append("No README file found")
            result.is_healthy = False
        # Check for LICENSE files
        result.has_license = False
        for license_name in LICENSE_FILES:
            file_url = f"{GITLAB_API_BASE}/projects/{owner}%2F{repo}/repository/files/{requests.utils.quote(license_name, safe='')}"
            params = {"ref": default_branch}
            file_response = requests.get(file_url, headers=headers, params=params)
            if file_response.status_code == 200:
                result.has_license = True
                break
        if policy.require_license and not result.has_license:
            result.warnings.append("No LICENSE file found")
            result.is_healthy = False
    except requests.exceptions.RequestException as e:
        # Handle network or API errors
        result.errors.append(f"Error checking GitLab repository: {str(e)}")
        result.is_healthy = False
    return result