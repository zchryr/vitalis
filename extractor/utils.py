from pathlib import Path
from typing import Union

def read_file_text(path: Union[str, Path]) -> str:
    """Read the entire contents of a text file.
    
    Args:
        path: File path as string or Path object.
        
    Returns:
        The complete file contents as a string.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
        PermissionError: If there are insufficient permissions to read the file.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()