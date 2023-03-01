"""Manages all path metadata."""
from pathlib import Path

######################################
# Shared file and subdirectory names #
######################################
METADATA_FILE_NAME = Path("metadata.yaml")

LOG_DIR = Path("logs")
LOG_FILE_NAME = Path("main_log.txt")
DETAILED_LOG_FILE_NAME = Path("main_log.json")

BEST_LINK = Path("best")
LATEST_LINK = Path("latest")
PRODUCTION_RUN = Path("production-runs")
