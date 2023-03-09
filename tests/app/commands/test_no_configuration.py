import pytest

from steamfitter.app import commands


GOOD_INVOCATIONS = [
    (commands.create_config, ["--help"]),
]


NO_CONFIG_FAILURES = [getattr(commands, c) for c in dir(commands)
                      if isinstance(getattr(commands, c), type) and c != 'create_config']

@pytest.fixture(params=[

])