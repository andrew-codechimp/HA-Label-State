"""Config flow for label_state integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import (
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_NOT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    DOMAIN,
    StateTypes,
)

STATE_TYPES = ["numeric_state", "state", "state_not"]

STATE_TO_UNAVAILABLE = "unavailable"
STATE_TO_UNKNOWN = "unknown"
STATE_ON = "on"
STATE_OFF = "off"
STATE_TO_OPTIONS = [STATE_TO_UNAVAILABLE, STATE_TO_UNKNOWN, STATE_ON, STATE_OFF]
STATE_NOT_OPTIONS = [STATE_ON, STATE_OFF]


OPTIONS_SCHEMA_NUMERIC_STATE = vol.Schema(
    {
        vol.Required(CONF_LABEL): selector.LabelSelector(),
        vol.Optional(CONF_STATE_LOWER_LIMIT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(CONF_STATE_UPPER_LIMIT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
    }
)

OPTIONS_SCHEMA_STATE = vol.Schema(
    {
        vol.Required(CONF_LABEL): selector.LabelSelector(),
        vol.Required(CONF_STATE_TO): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=STATE_TO_OPTIONS,
                translation_key="state_to",
                custom_value=True,
            )
        ),
    }
)

OPTIONS_SCHEMA_NOT_STATE = vol.Schema(
    {
        vol.Required(CONF_LABEL): selector.LabelSelector(),
        vol.Required(CONF_STATE_NOT): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=STATE_NOT_OPTIONS,
                translation_key="state_not",
                custom_value=True,
            )
        ),
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

CONFIG_SCHEMA_NOT_STATE = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
).extend(OPTIONS_SCHEMA_NOT_STATE.schema)


async def choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to label_type."""
    return cast(str, options["state_type"])


def _validate_upper_or_lower(options: dict[str, Any]) -> None:
    """Validate upper or lower limit."""
    upper_limit = options.get(CONF_STATE_UPPER_LIMIT)
    lower_limit = options.get(CONF_STATE_LOWER_LIMIT)

    if upper_limit is None and lower_limit is None:
        raise SchemaFlowError("upper_or_lower_not_specified")


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
        return {CONF_STATE_TYPE: state_type} | user_input

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
    StateTypes.NOT_STATE: SchemaFlowFormStep(
        CONFIG_SCHEMA_NOT_STATE,
        validate_user_input=validate_user_input(StateTypes.NOT_STATE),
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
    StateTypes.NOT_STATE: SchemaFlowFormStep(
        OPTIONS_SCHEMA_NOT_STATE,
        validate_user_input=validate_user_input(StateTypes.NOT_STATE),
    ),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Label State."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
