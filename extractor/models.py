from dataclasses import dataclass
from typing import Optional

@dataclass
class Dependency:
    name: str
    version: Optional[str] = None
    source: Optional[str] = None  # e.g., 'pypi', 'npm', 'conda', etc.
    raw: Optional[str] = None     # The raw line or entry from the manifest