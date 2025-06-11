from dataclasses import dataclass
from typing import Optional

@dataclass
class Dependency:
    """
    Represents a single dependency parsed from a manifest file.
    """
    name: str                        # Name of the dependency
    version: Optional[str] = None    # Version specifier (if any)
    source: Optional[str] = None     # Source type (e.g., 'pypi', 'npm', 'conda', etc.)
    raw: Optional[str] = None        # The raw line or entry from the manifest
