"""Constants for label_state."""

from enum import StrEnum
from logging import Logger, getLogger

from homeassistant.const import Platform

LOGGER: Logger = getLogger(__package__)

MIN_HA_VERSION = "2025.11"

DOMAIN = "label_state"
CONFIG_VERSION = 1

PLATFORMS = [Platform.BINARY_SENSOR]

CONF_LABEL = "label"
CONF_STATE_TYPE = "state_type"
CONF_STATE_TO = "state_to"
CONF_STATE_NOT = "state_not"
CONF_STATE_LOWER_LIMIT = "state_lower_limit"
CONF_STATE_UPPER_LIMIT = "state_upper_limit"

ATTR_ENTITIES = "entities"
ATTR_ENTITY_NAMES = "entity_names"
ATTR_LABEL_NAME = "label_name"


class StateTypes(StrEnum):
    """Available state types."""

    NUMERIC_STATE = "numeric_state"
    STATE = "state"
    NOT_STATE = "state_not"
