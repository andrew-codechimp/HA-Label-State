"""Test label_state config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.label_state.const import (
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_NOT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    DOMAIN,
)


@pytest.mark.parametrize(
    (
        "name",
        "state_type",
        "label",
        "state_to",
        "state_not",
        "state_lower_limit",
        "state_upper_limit",
    ),
    [
        (
            "Unavailable",
            "state",
            "my_label",
            "unavailable",
            None,
            None,
            None,
        ),
        (
            "On",
            "state_not",
            "my_label",
            None,
            "on",
            None,
            None,
        ),
        (
            "Numeric State",
            "numeric_state",
            "my_label",
            None,
            None,
            10,
            20,
        ),
    ],
)
async def test_config_flow(
    hass: HomeAssistant,
    name: str,
    state_type: str,
    label: str,
    state_to: str | None,
    state_not: str | None,
    state_lower_limit: float | None,
    state_upper_limit: float | None,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the config flow."""

    menu_step = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert menu_step.get("type") is FlowResultType.MENU
    assert menu_step.get("step_id") == "user"

    form_step = await hass.config_entries.flow.async_configure(
        menu_step["flow_id"],
        {"next_step_id": state_type},
    )

    if state_type == "numeric_state":
        result = await hass.config_entries.flow.async_configure(
            form_step["flow_id"],
            {
                CONF_NAME: name,
                CONF_LABEL: label,
                CONF_STATE_LOWER_LIMIT: state_lower_limit,
                CONF_STATE_UPPER_LIMIT: state_upper_limit,
            },
        )
    elif state_type == "state":
        result = await hass.config_entries.flow.async_configure(
            form_step["flow_id"],
            {
                CONF_NAME: name,
                CONF_LABEL: label,
                CONF_STATE_TO: state_to,
            },
        )
    elif state_type == "state_not":
        result = await hass.config_entries.flow.async_configure(
            form_step["flow_id"],
            {
                CONF_NAME: name,
                CONF_LABEL: label,
                CONF_STATE_NOT: state_not,
            },
        )

    await hass.async_block_till_done()

    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result.get("version") == 1

    if state_type == "numeric_state":
        assert result.get("options") == {
            CONF_NAME: name,
            CONF_STATE_TYPE: state_type,
            CONF_LABEL: label,
            CONF_STATE_LOWER_LIMIT: state_lower_limit,
            CONF_STATE_UPPER_LIMIT: state_upper_limit,
        }
    elif state_type == "state":
        assert result.get("options") == {
            CONF_NAME: name,
            CONF_STATE_TYPE: state_type,
            CONF_LABEL: label,
            CONF_STATE_TO: state_to,
        }
    elif state_type == "state_not":
        assert result.get("options") == {
            CONF_NAME: name,
            CONF_STATE_TYPE: state_type,
            CONF_LABEL: label,
            CONF_STATE_NOT: state_not,
        }

    assert len(mock_setup_entry.mock_calls) == 1
