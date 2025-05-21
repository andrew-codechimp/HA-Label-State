"""Constants for label_state."""

import json
from logging import Logger, getLogger
from pathlib import Path

from homeassistant.const import Platform

LOGGER: Logger = getLogger(__package__)

MIN_HA_VERSION = "2025.3"

manifestfile = Path(__file__).parent / "manifest.json"
with open(file=manifestfile, encoding="UTF-8") as json_file:
    manifest_data = json.load(json_file)

DOMAIN = manifest_data.get("domain")
NAME = manifest_data.get("name")
VERSION = manifest_data.get("version")
ISSUEURL = manifest_data.get("issue_tracker")
CONFIG_VERSION = 1

PLATFORMS = [Platform.SENSOR]

CONF_LABEL = "label"
CONF_STATE_FROM = "state_from"
CONF_STATE_TO = "state_to"
CONF_LOWER_LIMIT = "lower_limit"
CONF_UPPER_LIMIT = "upper_limit"

ATTR_LAST_MODIFIED = "last_modified"
