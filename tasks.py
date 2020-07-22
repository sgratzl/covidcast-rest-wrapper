"""
Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""
import shutil
import platform

from invoke import task

try:
    from pathlib import Path

    Path().expanduser()
except (ImportError, AttributeError):
    from pathlib2 import Path
import webbrowser


ROOT_DIR = Path(__file__).parent
SETUP_FILE = ROOT_DIR.joinpath("setup.py")
TEST_DIR = ROOT_DIR.joinpath("tests")
SOURCE_DIR = ROOT_DIR.joinpath("src")
DOCS_DIR = ROOT_DIR.joinpath("docs")
DOCS_BUILD_DIR = DOCS_DIR.joinpath("_build")
DOCS_INDEX = DOCS_BUILD_DIR.joinpath("index.html")
PYTHON_DIRS = [str(d) for d in [SOURCE_DIR]]


def _delete_file(file):
    try:
        file.unlink(missing_ok=True)
    except TypeError:
        # missing_ok argument added in 3.8
        try:
            file.unlink()
        except FileNotFoundError:
            pass


@task(help={"check": "Checks if source is formatted without applying changes"})
def format(c, check=False):
    """
    Format code
    """
    python_dirs_string = " ".join(PYTHON_DIRS)
    # Run yapf
    black_options = "--config pyproject.toml"
    c.run("black {} {}".format(black_options, python_dirs_string))


@task
def lint(c):
    """
    Lint code
    """
    c.run("pylint {}".format(SOURCE_DIR))


@task
def run(c):
    """
    Lint code
    """
    c.run("cd src && uvicorn main:app --reload")
