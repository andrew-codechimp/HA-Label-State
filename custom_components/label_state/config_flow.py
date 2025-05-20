"""Config flow for label_state integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.const import CONF_TYPE
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import CONF_LABEL, CONF_LOWER_LIMIT, CONF_STATE, CONF_UPPER_LIMIT, DOMAIN

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
        vol.Required(CONF_STATE): selector.TextSelector(),
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


LABEL_TYPES = [
    "numeric_state",
    "state",
]

CONFIG_FLOW = {
    "user": SchemaFlowMenuStep(LABEL_TYPES),
    "numeric_state": SchemaFlowFormStep(CONFIG_SCHEMA_NUMERIC_STATE),
    "state": SchemaFlowFormStep(CONFIG_SCHEMA_STATE),
}


async def choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to label_type."""
    return cast(str, options["label_type"])


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(next_step=choose_options_step),
    "numeric_state": SchemaFlowFormStep(OPTIONS_SCHEMA_NUMERIC_STATE),
    "state": SchemaFlowFormStep(OPTIONS_SCHEMA_STATE),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Label State."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
