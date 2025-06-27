import pytest
import json
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import tempfile
import os
import jsonschema

# Add the project root to the Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.cli import app

runner = CliRunner()

class TestJsonFormat:
    """Test the --format json functionality"""

    # JSON Schema for fallback output (since we only have basic extraction now)
    FALLBACK_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": ["string", "null"]},
                "source": {"type": ["string", "null"]},
                "raw": {"type": ["string", "null"]}
            },
            "required": ["name"]
        }
    }

    def test_json_format_basic_extraction(self):
        """Test JSON format output with basic extraction"""
        # Create a test requirements file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('requests==2.25.0\ndjango==3.2.0\n')

            result = runner.invoke(app, ['extract', test_file, '--format', 'json'])

            assert result.exit_code == 0

            # Parse JSON output
            try:
                output_json = json.loads(result.output.strip())
            except json.JSONDecodeError as e:
                pytest.fail(f"Output is not valid JSON: {e}")

            # Validate against fallback schema
            try:
                jsonschema.validate(output_json, self.FALLBACK_SCHEMA)
            except jsonschema.ValidationError as e:
                pytest.fail(f"JSON output doesn't match expected schema: {e}")

            # Verify specific structure
            assert len(output_json) == 2
            assert output_json[0]["name"] == "requests"
            assert output_json[1]["name"] == "django"

    def test_human_format_default(self):
        """Test that human format is used by default (no breaking changes)"""
        # Create a test requirements file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('requests==2.25.0\n')

            result = runner.invoke(app, ['extract', test_file])

            assert result.exit_code == 0

            # Verify human-readable output (not JSON)
            assert "Basic Dependency Extraction" in result.output
            assert "Found" in result.output
            assert "=" in result.output  # Header separators

            # Should not be valid JSON
            with pytest.raises(json.JSONDecodeError):
                json.loads(result.output.strip())

    def test_human_format_explicit(self):
        """Test explicit human format option"""
        # Create a test requirements file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            with open(test_file, 'w') as f:
                f.write('requests==2.25.0\n')

            result = runner.invoke(app, ['extract', test_file, '--format', 'human'])

            assert result.exit_code == 0

            # Verify human-readable output
            assert "Basic Dependency Extraction" in result.output
            assert "Found" in result.output

    def test_json_format_help_text(self):
        """Test that help text documents the --format option"""
        result = runner.invoke(app, ['extract', '--help'])

        assert result.exit_code == 0
        # Strip ANSI color codes for reliable string matching
        import re
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.output)
        assert '--format' in clean_output
        assert 'human or json' in clean_output
        assert 'default: human' in clean_output

    def test_json_format_with_file_write_and_validation(self):
        """Integration test: write JSON to file and validate with schema"""
        # Create a test requirements file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'requirements.txt')
            output_file = os.path.join(temp_dir, 'analysis.json')

            with open(test_file, 'w') as f:
                f.write('requests==2.25.0\n')

            # Run command and capture output to file
            result = runner.invoke(app, ['extract', test_file, '--format', 'json'])

            assert result.exit_code == 0

            # Write output to file
            with open(output_file, 'w') as f:
                f.write(result.output.strip())

            # Read and validate the file
            with open(output_file, 'r') as f:
                file_content = json.load(f)

            # Validate against schema
            jsonschema.validate(file_content, self.FALLBACK_SCHEMA)

            # Verify content
            assert file_content[0]["name"] == "requests"

    def test_health_command(self):
        """Test that health command works"""
        result = runner.invoke(app, ['health'])

        assert result.exit_code == 0
        assert 'Vitalis CLI is healthy!' in result.output

    def test_health_command_help_text(self):
        """Test that health command help text is properly documented"""
        result = runner.invoke(app, ['health', '--help'])

        assert result.exit_code == 0
        assert 'Check the health of the vitalis CLI' in result.output