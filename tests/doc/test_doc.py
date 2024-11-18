# Test examples from documentation
import os
import subprocess
from pathlib import Path
import pytest

PYTHON = Path(__file__).parents[2] / ".venv/Scripts/python.exe"

# Examples require C:\Scade One. check if it is installed
s_one_install = "C:/Scade One"
s_one_exists = Path(s_one_install).exists()


def check_example(example: Path):
    """Check if example requires 's_one_install'"""
    with example.open() as fd:
        for line in fd:
            if line.find(s_one_install) > 0:
                return s_one_exists
    return True


def collect():
    """Collect Python files in documentation tree"""
    # Root directory for doc tree analysis
    doc_root = "doc/source"
    # Python files to skip
    skip = "conf.py"
    examples = []
    for dirpath, _, files in os.walk(doc_root):
        examples.extend(
            os.path.join(dirpath, f) for f in files if f[-3:] == ".py" and f not in skip
        )
    return examples


class TestDocumentation:

    @pytest.mark.parametrize(
        "example",
        collect(),
    )
    def test_example(self, example, capsys):
        if check_example(Path(example)):
            proc = subprocess.run([PYTHON, example])
            assert proc.returncode == 0
        else:
            with capsys.disabled():
                print(f"Example {example} requires Scade One")
