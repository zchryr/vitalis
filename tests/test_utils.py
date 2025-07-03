import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.utils import read_file_text


class TestUtils:
    """Test utility functions"""

    def test_read_file_text_str_path(self):
        """Test reading file with string path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.txt')
            test_content = "Hello, World!\nThis is a test file."
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)

            result = read_file_text(test_file)
            assert result == test_content

    def test_read_file_text_path_object(self):
        """Test reading file with Path object"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / 'test.txt'
            test_content = "Hello, World!\nThis is a test file."
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)

            result = read_file_text(test_file)
            assert result == test_content

    def test_read_file_text_utf8_encoding(self):
        """Test reading file with UTF-8 encoding"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.txt')
            test_content = "Hello, 世界! 🌍"
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)

            result = read_file_text(test_file)
            assert result == test_content

    def test_read_file_text_empty_file(self):
        """Test reading empty file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'empty.txt')
            
            with open(test_file, 'w', encoding='utf-8') as f:
                pass  # Create empty file

            result = read_file_text(test_file)
            assert result == ""

    def test_read_file_text_file_not_found(self):
        """Test reading non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            read_file_text("/non/existent/file.txt")