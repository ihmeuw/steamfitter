SOURCE_COLUMNS = '''columns:
  - name: "column_name1"               # The name of the expected column
    data_type: "column_data_type"      # One of [str, int, float, bool, datetime]
    description: "Column description"  # A description of the column
    is_nullable: True                  # True or False, whether the column can contain null values
    members: []                        # A list of the possible values for the column, if it is categorical. Ignored if empty.
  - name: "column_name2" 
    data_type: "column_data_type" 
    description: "Column description" 
    is_nullable: True 
    members: [] 
'''


EXTRACTION = '''"""Extraction template for {source_name}."""
from pathlib import Path

import pandas as pd
import click

from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(output_root: Path):
    """Run the extraction pipeline for {source_name}."""
    extract_data(output_root)
    format_data(output_root)
    

def extract_data(output_root: Path):
    """Extract data from the source."""
    # E.g.:
    url = "https://example.com/data.csv"
    df = pd.read_csv(url)
    df.to_csv(output_root / "raw_data.csv", index=False)


def format_data(output_root: Path):
    """Format data for use in the project."""
    # E.g.:
    df = pd.read_csv(output_root / "raw_data.csv")
    # ... data formatting code ...
    df.to_csv(output_root / "formatted_data.csv")


@click.command
@click.option("--output-root", type=click.Path(exists=True), default=".")
@click_options.verbose_and_with_debugger
def main(output_root: str, verbose: int, with_debugger: bool):
    """Extract and format data from the source."""
    output_root = Path(output_root)
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(output_root)
        
    
if __name__ == "__main__":
    main()
'''

GITIGNORE = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
*.pyc
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/

# Pycharm project settings
.idea/

# Local user jupyter notebooks directory
notebooks/

# Data files
*.csv
*.hdf
*.hdf5
*.parquet

"""
