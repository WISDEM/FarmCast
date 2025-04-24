import os
import pytest
import subprocess

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../examples")

@pytest.mark.parametrize("example_script", [
    "generate_runs.py",
])
def test_example_scripts(example_script):
    """
    Test that example scripts run without errors.
    """
    script_path = os.path.join(EXAMPLES_DIR, example_script)
    assert os.path.exists(script_path), f"Example script {example_script} does not exist."

    # Run the script and check for errors
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script {example_script} failed with error: {result.stderr}"
