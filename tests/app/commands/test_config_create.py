from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.lib.testing import invoke_cli





# def test_config_create_with_existing_config(config_path, projects_root):
#     config_path.touch()
#     assert config_path.exists()
#
#     result = invoke_cli(commands.create_config, [str(projects_root)], exit_zero=False)
#
#     assert result.exit_code == 1
#     assert "Configuration file already exists" in result.output
#     assert "Aborting" in result.output






