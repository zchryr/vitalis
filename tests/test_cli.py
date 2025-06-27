import pytest
import json
import requests
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

class TestPolicyOption:
    """Test the --policy option functionality"""
    
    def test_extract_with_default_policy(self):
        """Test that extract command uses default policy value of 365 days"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {"analysis": "mock_result"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file with proper name
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file])
                
                # Verify the request was made with default policy
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                payload = kwargs['json']
                
                assert payload['policy']['max_inactive_days'] == 365
                assert result.exit_code == 0
    
    def test_extract_with_custom_policy(self):
        """Test that extract command uses custom policy value when --policy is specified"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {"analysis": "mock_result"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file with proper name
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file, '--policy', '180'])
                
                # Verify the request was made with custom policy
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                payload = kwargs['json']
                
                assert payload['policy']['max_inactive_days'] == 180
                assert result.exit_code == 0
    
    def test_extract_with_policy_fallback_on_connection_error(self):
        """Test that extract command falls back to basic extraction when analyzer service is unavailable"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock connection error
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            # Create a test requirements file with proper name
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file, '--policy', '180'])
                
                # Should still succeed with fallback
                assert result.exit_code == 0
                assert "Warning: Analyzer service not available" in result.output
    
    def test_help_text_includes_policy_option(self):
        """Test that help text documents the --policy flag"""
        result = runner.invoke(app, ['extract', '--help'])
        
        assert result.exit_code == 0
        assert '--policy' in result.output
        assert 'Max inactive days threshold' in result.output
        assert 'default: 365' in result.output
    
    def test_health_command_help_text(self):
        """Test that health command help text is properly documented"""
        result = runner.invoke(app, ['health', '--help'])
        
        assert result.exit_code == 0
        assert 'Check the health of the vitalis CLI' in result.output

class TestAnalyzerIntegration:
    """Test analyzer service integration"""
    
    def test_analyzer_payload_structure(self):
        """Test that the analyzer service receives properly structured payload"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response  
            mock_response = MagicMock()
            mock_response.json.return_value = {"analysis": "test"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file with proper name
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\ndjango==3.2.0\n')
                
                result = runner.invoke(app, ['extract', test_file, '--policy', '90'])
                
                # Verify payload structure
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                
                assert kwargs['json']['manifest_content'] == 'requests==2.25.0\ndjango==3.2.0\n'
                assert kwargs['json']['manifest_type'] == 'requirements.txt'
                assert kwargs['json']['policy'] == {
                    'max_inactive_days': 90,
                    'require_license': True,
                    'require_readme': True
                }
                
                assert result.exit_code == 0

class TestJsonFormat:
    """Test the --format json functionality"""
    
    # JSON Schema for full analysis output
    FULL_ANALYSIS_SCHEMA = {
        "type": "object",
        "properties": {
            "dependencies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": ["string", "null"]},
                        "source": {"type": ["string", "null"]},
                        "raw": {"type": ["string", "null"]},
                        "health": {
                            "type": "object",
                            "properties": {
                                "is_healthy": {"type": "boolean"},
                                "has_readme": {"type": "boolean"},
                                "has_license": {"type": "boolean"},
                                "warnings": {"type": "array", "items": {"type": "string"}},
                                "errors": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["is_healthy", "has_readme", "has_license", "warnings", "errors"]
                        }
                    },
                    "required": ["name"]
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "total_dependencies": {"type": "integer"},
                    "healthy_count": {"type": "integer"},
                    "unhealthy_count": {"type": "integer"}
                },
                "required": ["total_dependencies", "healthy_count", "unhealthy_count"]
            },
            "policy": {
                "type": "object",
                "properties": {
                    "max_inactive_days": {"type": "integer"},
                    "require_license": {"type": "boolean"},
                    "require_readme": {"type": "boolean"}
                },
                "required": ["max_inactive_days", "require_license", "require_readme"]
            }
        },
        "required": ["dependencies"]
    }
    
    # JSON Schema for fallback output
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
    
    def test_json_format_full_analysis(self):
        """Test JSON format output with full analysis"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response with realistic structure
            mock_response = MagicMock()
            mock_analysis = {
                "dependencies": [
                    {
                        "name": "requests",
                        "version": "2.25.0",
                        "source": "pypi",
                        "raw": "requests==2.25.0",
                        "health": {
                            "is_healthy": True,
                            "repository_url": "https://github.com/psf/requests",
                            "platform": "github",
                            "owner": "psf",
                            "repo_name": "requests",
                            "has_readme": True,
                            "has_license": True,
                            "warnings": [],
                            "errors": []
                        }
                    }
                ],
                "summary": {
                    "total_dependencies": 1,
                    "healthy_count": 1,
                    "unhealthy_count": 0
                },
                "policy": {
                    "max_inactive_days": 365,
                    "require_license": True,
                    "require_readme": True
                }
            }
            mock_response.json.return_value = mock_analysis
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file, '--format', 'json'])
                
                assert result.exit_code == 0
                
                # Parse JSON output
                try:
                    output_json = json.loads(result.output.strip())
                except json.JSONDecodeError as e:
                    pytest.fail(f"Output is not valid JSON: {e}")
                
                # Validate against schema
                try:
                    jsonschema.validate(output_json, self.FULL_ANALYSIS_SCHEMA)
                except jsonschema.ValidationError as e:
                    pytest.fail(f"JSON output doesn't match expected schema: {e}")
                
                # Verify specific structure
                assert "dependencies" in output_json
                assert len(output_json["dependencies"]) == 1
                assert output_json["dependencies"][0]["name"] == "requests"
    
    def test_json_format_fallback(self):
        """Test JSON format output with fallback extraction"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock connection error to trigger fallback
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
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
                    pytest.fail(f"JSON output doesn't match expected fallback schema: {e}")
                
                # Verify specific structure
                assert len(output_json) == 2
                assert output_json[0]["name"] == "requests"
                assert output_json[1]["name"] == "django"
    
    def test_human_format_default(self):
        """Test that human format is used by default (no breaking changes)"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "dependencies": [{"name": "requests", "version": "2.25.0"}],
                "summary": {"total_dependencies": 1, "healthy_count": 1, "unhealthy_count": 0}
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file])
                
                assert result.exit_code == 0
                
                # Verify human-readable output (not JSON)
                assert "🔍 Dependency Analysis Report" in result.output
                assert "📦 Found" in result.output
                assert "=" in result.output  # Header separators
                
                # Should not be valid JSON
                with pytest.raises(json.JSONDecodeError):
                    json.loads(result.output.strip())
    
    def test_human_format_explicit(self):
        """Test explicit human format option"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "dependencies": [{"name": "requests", "version": "2.25.0"}],
                "summary": {"total_dependencies": 1, "healthy_count": 1, "unhealthy_count": 0}
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create a test requirements file
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, 'requirements.txt')
                with open(test_file, 'w') as f:
                    f.write('requests==2.25.0\n')
                
                result = runner.invoke(app, ['extract', test_file, '--format', 'human'])
                
                assert result.exit_code == 0
                
                # Verify human-readable output
                assert "🔍 Dependency Analysis Report" in result.output
                assert "📦 Found" in result.output
    
    def test_json_format_help_text(self):
        """Test that help text documents the --format option"""
        result = runner.invoke(app, ['extract', '--help'])
        
        assert result.exit_code == 0
        assert '--format' in result.output
        assert 'human or json' in result.output
        assert 'default: human' in result.output
    
    def test_json_format_with_file_write_and_validation(self):
        """Integration test: write JSON to file and validate with schema"""
        with patch('extractor.cli.requests.post') as mock_post:
            # Mock successful response
            mock_response = MagicMock()
            mock_analysis = {
                "dependencies": [
                    {
                        "name": "requests",
                        "version": "2.25.0",
                        "source": "pypi", 
                        "raw": "requests==2.25.0",
                        "health": {
                            "is_healthy": True,
                            "has_readme": True,
                            "has_license": True,
                            "warnings": [],
                            "errors": []
                        }
                    }
                ],
                "summary": {
                    "total_dependencies": 1,
                    "healthy_count": 1,
                    "unhealthy_count": 0
                },
                "policy": {
                    "max_inactive_days": 365,
                    "require_license": True,
                    "require_readme": True
                }
            }
            mock_response.json.return_value = mock_analysis
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
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
                jsonschema.validate(file_content, self.FULL_ANALYSIS_SCHEMA)
                
                # Verify content
                assert file_content["dependencies"][0]["name"] == "requests"