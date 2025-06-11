from pathlib import Path
from typing import Union

def read_file_text(path: Union[str, Path]) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()