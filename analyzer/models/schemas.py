from pydantic import BaseModel
from typing import List, Optional

class HealthCheckResult(BaseModel):
    """
    Represents the result of a health check for a repository, including metadata and health status.
    """
    repository_url: str  # URL of the repository
    platform: str        # Platform name (e.g., 'github', 'gitlab')
    owner: str           # Owner or organization of the repository
    repo_name: str       # Repository name
    last_activity: Optional[str] = None  # ISO 8601 timestamp of last activity
    days_since_last_activity: Optional[int] = None  # Days since last activity
    open_issues_count: Optional[int] = None  # Number of open issues
    stars_count: Optional[int] = None        # Number of stars
    forks_count: Optional[int] = None        # Number of forks
    has_readme: bool = False                 # Whether a README file exists
    has_license: bool = False                # Whether a LICENSE file exists
    warnings: List[str] = []                 # List of warnings
    errors: List[str] = []                   # List of errors
    is_healthy: bool = True                  # Health status

class HealthCheckResponse(BaseModel):
    """
    Response model for a batch of health check results.
    """
    results: List[HealthCheckResult]

class RepoCheckRequest(BaseModel):
    """
    Request model for checking a single repository by URL or local path.
    """
    repository_url: Optional[str] = None  # URL of the repository
    repository_path: Optional[str] = None # Local path to the repository

class RepoBatchCheckRequest(BaseModel):
    """
    Request model for checking multiple repositories in batch.
    """
    repos: List[RepoCheckRequest]

class PackageInfo(BaseModel):
    """
    Metadata about a package, including repository and version info.
    """
    name: str
    summary: Optional[str] = None
    repository_url: Optional[str] = None
    repository_platform: Optional[str] = None
    repository_org: Optional[str] = None
    repository_name: Optional[str] = None
    latest_version: Optional[str] = None
    created_date: Optional[str] = None
    error: bool = False

class PackageResponse(BaseModel):
    """
    Response model for a batch of package info results.
    """
    packages: List[PackageInfo]

class Policy(BaseModel):
    """
    Policy settings for repository health checks.
    """
    max_inactive_days: int = 365      # Max days of inactivity before warning
    require_license: bool = True      # Whether a LICENSE file is required
    require_readme: bool = True       # Whether a README file is required

class AnalysisRequest(BaseModel):
    """
    Request model for analyzing a manifest file.
    """
    manifest_content: str             # The content of the manifest file
    manifest_type: str                # Manifest type (e.g., 'requirements.txt', 'package.json')
    policy: Policy = Policy()         # Policy to use for analysis