"""
This module exposes the main data models for dependencies, schemas, and API interfaces.
"""
from core.models import Dependency  # Dependency data class
from .schemas import (
    HealthCheckResult,      # Result of a repository health check
    HealthCheckResponse,    # Response for batch health checks
    RepoCheckRequest,       # Request for a single repo check
    RepoBatchCheckRequest,  # Request for batch repo checks
    PackageInfo,            # Metadata about a package
    PackageResponse,        # Response for batch package info
    Policy,                 # Policy settings for health checks
    AnalysisRequest         # Request for manifest analysis
)

# Expose all main model classes for import
__all__ = [
    'Dependency',
    'HealthCheckResult',
    'HealthCheckResponse',
    'RepoCheckRequest',
    'RepoBatchCheckRequest',
    'PackageInfo',
    'PackageResponse',
    'Policy',
    'AnalysisRequest'
]