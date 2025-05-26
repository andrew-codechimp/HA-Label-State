"""Test label_state config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.components.template import async_setup_entry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.label_state.const import (
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
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
        ),
        (
            "Numeric State",
            "state_numeric",
            "my_label",
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
    state_lower_limit: float | None,
    state_upper_limit: float | None,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the config flow."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.MENU

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step": state_type},
    )

    with patch(
        "homeassistant.components.template.async_setup_entry", wraps=async_setup_entry
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: name,
                CONF_STATE_TYPE: state_type,
                CONF_LABEL: label,
                CONF_STATE_TO: state_to,
                CONF_STATE_LOWER_LIMIT: state_lower_limit,
                CONF_STATE_UPPER_LIMIT: state_upper_limit,
            },
        )
        await hass.async_block_till_done()

    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result.get("version") == 1
    assert result.get("options") == {
        CONF_NAME: name,
        CONF_STATE_TYPE: state_type,
        CONF_LABEL: label,
        CONF_STATE_TO: state_to,
        CONF_STATE_LOWER_LIMIT: state_lower_limit,
        CONF_STATE_UPPER_LIMIT: state_upper_limit,
    }

    assert len(mock_setup_entry.mock_calls) == 1
