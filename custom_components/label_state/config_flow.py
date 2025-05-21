"""Config flow for label_state integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Mapping
from enum import StrEnum
from typing import Any, cast

import voluptuous as vol
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import (
    CONF_LABEL,
    CONF_LOWER_LIMIT,
    CONF_STATE_FROM,
    CONF_STATE_TO,
    CONF_UPPER_LIMIT,
    DOMAIN,
)

STATE_TYPES = [
    "numeric_state",
    "state",
]


class StateTypes(StrEnum):
    """Available state types."""

    NUMERIC_STATE = "numeric_state"
    STATE = "state"


OPTIONS_SCHEMA_NUMERIC_STATE = vol.Schema(
    {
        vol.Required(CONF_LABEL): selector.LabelSelector(),
        vol.Optional(CONF_LOWER_LIMIT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(CONF_UPPER_LIMIT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
    }
)

OPTIONS_SCHEMA_STATE = vol.Schema(
    {
        vol.Required(CONF_LABEL): selector.LabelSelector(),
        vol.Optional(CONF_STATE_FROM): selector.TextSelector(),
        vol.Optional(CONF_STATE_TO): selector.TextSelector(),
    }
)

CONFIG_SCHEMA_NUMERIC_STATE = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
).extend(OPTIONS_SCHEMA_NUMERIC_STATE.schema)

CONFIG_SCHEMA_STATE = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
).extend(OPTIONS_SCHEMA_STATE.schema)


async def choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to label_type."""
    return cast(str, options["state_type"])


def _validate_upper_or_lower(options: dict[str, Any]) -> None:
    """Validate upper or lower limit."""
    upper_limit = options.get(CONF_UPPER_LIMIT)
    lower_limit = options.get(CONF_LOWER_LIMIT)

    if upper_limit is None and lower_limit is None:
        raise vol.Invalid("An upper or lower limit must be set")


def _validate_from_or_to(options: dict[str, Any]) -> None:
    """Validate upper or lower limit."""
    state_from = options.get(CONF_STATE_FROM)
    state_to = options.get(CONF_STATE_TO)

    if state_from is None and state_to is None:
        raise vol.Invalid("An from or to must be specified")


def validate_user_input(
    state_type: str,
) -> Callable[
    [SchemaCommonFlowHandler, dict[str, Any]],
    Coroutine[Any, Any, dict[str, Any]],
]:
    """Do post validation of user input.

    For numeric state: Validate an upper or lower limit is set.
    For state: Validate a from or to is set.
    For all domaines: Set state type.
    """

    async def _validate_user_input(
        _: SchemaCommonFlowHandler,
        user_input: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate based on label type and add label type to user input."""
        if state_type == StateTypes.NUMERIC_STATE:
            _validate_upper_or_lower(user_input)
        if state_type == StateTypes.STATE:
            _validate_from_or_to(user_input)
        return {"state_type": state_type} | user_input

    return _validate_user_input


CONFIG_FLOW = {
    "user": SchemaFlowMenuStep(STATE_TYPES),
    StateTypes.NUMERIC_STATE: SchemaFlowFormStep(
        CONFIG_SCHEMA_NUMERIC_STATE,
        validate_user_input=validate_user_input(StateTypes.NUMERIC_STATE),
    ),
    StateTypes.STATE: SchemaFlowFormStep(
        CONFIG_SCHEMA_STATE,
        validate_user_input=validate_user_input(StateTypes.STATE),
    ),
}


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(next_step=choose_options_step),
    StateTypes.NUMERIC_STATE: SchemaFlowFormStep(
        OPTIONS_SCHEMA_NUMERIC_STATE,
        validate_user_input=validate_user_input(StateTypes.NUMERIC_STATE),
    ),
    StateTypes.STATE: SchemaFlowFormStep(
        OPTIONS_SCHEMA_STATE, validate_user_input=validate_user_input(StateTypes.STATE)
    ),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Label State."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
