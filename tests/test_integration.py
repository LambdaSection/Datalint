"""
Integration tests for CLI commands.
"""

import subprocess
import tempfile
import os
import json


class TestCLI:
    def test_validate_command(self):
        """Test basic validate command execution."""
        csv_content = "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            result = subprocess.run(
                ['datalint', 'validate', csv_path],
                capture_output=True, text=True
            )

            assert result.returncode == 0
            assert "DataLint Validation Report" in result.stdout
            assert "[PASS]" in result.stdout or "passed" in result.stdout

        finally:
            os.unlink(csv_path)

    def test_json_output(self):
        """Test JSON output format."""
        csv_content = "a,b\n1,2\n3,4\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            result = subprocess.run(
                ['datalint', 'validate', csv_path, '--format', 'json'],
                capture_output=True, text=True
            )

            assert result.returncode == 0
            # JSON output includes "Loaded dataset:" line before JSON
            # Extract the JSON portion
            stdout_lines = result.stdout.strip().split('\n')
            json_start = next(i for i, line in enumerate(stdout_lines) if line.startswith('{'))
            json_content = '\n'.join(stdout_lines[json_start:])

            output = json.loads(json_content)
            assert 'summary' in output
            assert 'results' in output
            assert output['summary']['total'] == 5  # 5 validators

        finally:
            os.unlink(csv_path)

    def test_profile_learn(self):
        """Test profile learning command."""
        csv_content = "value,category\n1.0,A\n2.0,B\n3.0,A\n4.0,B\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as pf:
            profile_path = pf.name

        try:
            result = subprocess.run(
                ['datalint', 'profile', csv_path, '--learn', '--output', profile_path],
                capture_output=True, text=True
            )

            assert result.returncode == 0
            assert "Profile saved" in result.stdout

            # Verify profile file has content
            with open(profile_path, 'r') as f:
                profile_data = json.load(f)
            assert 'column_profiles' in profile_data

        finally:
            os.unlink(csv_path)
            if os.path.exists(profile_path):
                os.unlink(profile_path)