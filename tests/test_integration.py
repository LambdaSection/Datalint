import subprocess
import tempfile
import os
from pathlib import Path

class TestCLI:
    def test_validate_command(self):
        # Create test CSV
        csv_content = "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            # Run CLI command
            result = subprocess.run(
                ['datalint', 'validate', csv_path],
                capture_output=True, text=True
            )

            assert result.returncode == 0
            assert "3 passed" in result.stdout
            assert "✅" in result.stdout

        finally:
            os.unlink(csv_path)

    def test_json_output(self):
        csv_content = "a,b\n1,2\n3,4\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            result = subprocess.run(
                ['datalint', 'validate', csv_path, '--format', 'json'],
                capture_output=True, text=True
            )

            import json
            output = json.loads(result.stdout)
            assert 'missing_values' in output
            assert 'data_types' in output

        finally:
            os.unlink(csv_path)