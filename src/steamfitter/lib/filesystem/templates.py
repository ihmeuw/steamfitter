

EXTRACTION = '''
"""Extraction template for {source_name}."""
import click

def extract_data(output_root: Path):
    """Extract data from the source."""
    pass


def format_data(output_root: Path):
    """Format data for use in the project."""
    # E.g.:
    df = pd.read_csv(output_root / "raw_data.csv")
    # ... data formatting code ...
    df.to_csv(output_root / "formatted_data.csv")


def validate_data(output_root: Path):
    """Validate data for use in the project."""
    schema = [
        # (column_name, column_type, is_nullable)
        ("column_1", int, True),
        ("column_2", str, True),
        ("column_3", float, False),
    ]

    df = pd.read_csv(output_root / "formatted_data.csv")
    extra = df.columns.difference({{column_name for column_name, _, _ in schema}})
    missing = {{column_name for column_name, _, _ in schema}}.difference(df.columns)
    if extra:
        raise ValueError(f"Data contains unexpected columns: {{extra}}")
    if missing:
        raise ValueError(f"Data is missing columns: {{missing}}")

    for column_name, column_type, is_nullable in schema:
        if column_name not in df.columns:
            raise ValueError(f"Column {{column_name}} not found in data.")
        if not is_nullable and df[column_name].isnull().any():
            raise ValueError(f"Column {{column_name}} contains null values.")
        if df[column_name].dtype != column_type:
            raise ValueError(f"Column {{column_name}} is not of type {{column_type}}.")


@click.command(name=extract_{source_name})
@click.option("--output-root", type=click.Path(exists=True), default=".")
def main(output_root: Path):
    """Extract and format data from the source."""
    extract_data(output_root)
    format_data(output_root)

'''

GITIGNORE = '''
# Byte-compiled / optimized / DLL files
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

# metadata files
metadata.yaml

# Versioned data directories
*/*/***

'''
