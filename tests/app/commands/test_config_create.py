from pathlib import Path

from click.testing import CliRunner
import pytest

from steamfitter.app.commands.config_create import create_config
from steamfitter.app.configuration import Configuration
from steamfitter.lib.io import yaml


def test_config_create(tmpdir):
    config_path = Path(tmpdir) / "config.yaml"
    project_root = Path(tmpdir) / "tests/app/projects"

    assert not config_path.exists()
    assert not project_root.exists()

    runner = CliRunner()
    result = runner.invoke(create_config, [str(project_root)])

    assert result.exit_code == 0

    assert config_path.exists()
    assert project_root.exists()

    config = Configuration()
    assert config.projects_root == project_root
    assert config.projects == {}
    assert config.default_project == ""

    assert f"Projects root {str(project_root)} does not exist" in result.output
    assert "Configuration file written to" in result.output
    assert str(config_path) in result.output


def test_config_create_with_existing_config(tmpdir):

    config_path = Path(tmpdir) / "config.yaml"
    project_root = Path(tmpdir) / "tests/app/projects"

    config_path.touch()
    assert config_path.exists()

    runner = CliRunner()
    result = runner.invoke(create_config, [str(project_root)])

    assert result.exit_code == 1
    assert "Configuration file already exists" in result.output
    assert "Aborting" in result.output


def test_config_create_with_existing_projects_root(tmpdir):
    config_path = Path(tmpdir) / "config.yaml"
    project_root = Path(tmpdir) / "tests/app/projects"

    project_root.mkdir(parents=True)
    assert project_root.exists()

    runner = CliRunner()
    result = runner.invoke(create_config, [str(project_root)])

    assert result.exit_code == 0
    assert "Configuration file written to" in result.output
    assert str(config_path) in result.output

    config = Configuration()
    assert config.projects_root == project_root
    assert config.projects == {}
    assert config.default_project == ""

    assert "Projects root" not in result.output


def test_config_create_with_existing_projects(tmpdir):
    config_path = Path(tmpdir) / "config.yaml"
    project_root = Path(tmpdir) / "tests/app/projects"

    project_root.mkdir(parents=True)
    assert project_root.exists()

    project_dir = project_root / "project"
    project_dir.mkdir()
    project_metadata_file = project_dir / "metadata.yaml"
    project_metadata = {"name": "project", "directory_type": "project"}
    yaml.dump(project_metadata_file, project_metadata)

    runner = CliRunner()
    result = runner.invoke(create_config, [str(project_root)])

    assert result.exit_code == 0
    assert "Configuration file written to" in result.output
    assert str(config_path) in result.output

    config = Configuration()
    assert config.projects_root == project_root
    assert config.projects == {0: "project"}
    assert config.default_project == ""

    assert "Projects root" not in result.output
