import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """Fixture to capture loguru logs in pytest tests."""
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
