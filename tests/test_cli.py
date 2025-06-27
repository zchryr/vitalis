import pytest
import json
import requests
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import tempfile
import os

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