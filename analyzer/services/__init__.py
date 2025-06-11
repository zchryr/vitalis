"""
This module exposes the main service modules for dependency extraction, package info, and repository health checks.
"""
from . import dependency_extractor   # Functions for extracting dependencies from manifests
from . import package_info           # Functions for fetching and parsing package metadata
from . import repo_health            # Functions for checking repository health

# Expose all main service modules for import
__all__ = ['dependency_extractor', 'package_info', 'repo_health']